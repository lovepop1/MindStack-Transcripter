from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from youtube_transcript_api import YouTubeTranscriptApi

app = FastAPI(title="MindStack Transcript Service")

# Allow requests from the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "MindStack Python Microservice is running"}

@app.get("/api/transcript")
def get_transcript(v: str = None, start: float = None, end: float = None):
    if not v:
        return JSONResponse(status_code=400, content={"error": "Missing video ID parameter 'v'"})
    
    print(f"[Transcript Request] Video ID: {v}, Start: {start}, End: {end}")
        
    try:
        # Some versions/environments of youtube-transcript-api use different base methods
        full_text = ""
        
        # Universal attribute getter for dicts vs objects
        def get_val(item, key):
            if isinstance(item, dict):
                return item.get(key)
            return getattr(item, key, None)
        
        try:
            # Try newer functional approach if available (common in pip 3.11+)
            from youtube_transcript_api import YouTubeTranscriptApi as yta
            if hasattr(yta, 'get_transcript'):
                print(f"[Transcript] Using functional API approach")
                data = yta.get_transcript(v, languages=['en', 'en-US', 'en-GB', 'hi'])
                
                if start is not None and end is not None:
                    buffered_start = max(0, start - 15)
                    buffered_end = end + 15
                    filtered_segments = [
                        get_val(s, 'text') for s in data 
                        if (get_val(s, 'start') + get_val(s, 'duration')) >= buffered_start 
                        and get_val(s, 'start') <= buffered_end
                    ]
                    if not filtered_segments:
                        print(f"[Transcript] No segments in time window, using full transcript")
                        filtered_segments = [get_val(s, 'text') for s in data]
                    else:
                        print(f"[Transcript] Found {len(filtered_segments)} segments in time window")
                else:
                    filtered_segments = [get_val(s, 'text') for s in data]
                    print(f"[Transcript] Using full transcript: {len(filtered_segments)} segments")
                
                full_text = " ".join(filtered_segments)
                print(f"[Transcript] ✅ Success: {len(full_text)} characters")
                return {"transcript": full_text}
        except Exception as dynamic_err:
            print(f"[Transcript] Functional API failed: {str(dynamic_err)}, trying OOP approach")
            pass # Fallback to Object-Oriented extraction
            
        # Object-Oriented extraction for versions like 0.6.x - 1.2.x
        print(f"[Transcript] Using OOP API approach")
        ytt_api = YouTubeTranscriptApi()
        
        if hasattr(ytt_api, 'list'):
            transcript_list = ytt_api.list(v)
        elif hasattr(ytt_api, 'list_transcripts'):
            transcript_list = ytt_api.list_transcripts(v)
        else:
            error_msg = "Incompatible youtube-transcript-api version. Neither list() nor get_transcript() found."
            print(f"[Transcript] ❌ {error_msg}")
            return JSONResponse(status_code=500, content={"error": error_msg})
        
        try:
            # First try to find manual transcripts
            transcript = transcript_list.find_manually_created_transcript(['en', 'en-US', 'en-GB', 'hi'])
            print(f"[Transcript] Using manually created transcript")
        except Exception:
            # Fallback to generated
            try:
                transcript = transcript_list.find_generated_transcript(['en', 'en-US', 'en-GB', 'hi'])
                print(f"[Transcript] Using auto-generated transcript")
            except Exception:
                # Absolute fallback
                transcript = next(iter(transcript_list))
                print(f"[Transcript] Using first available transcript")
            
        data = transcript.fetch()

        if start is not None and end is not None:
            # Add a 15-second buffer before and after for optimal context
            buffered_start = max(0, start - 15)
            buffered_end = end + 15
            
            filtered_segments = [
                get_val(segment, 'text') for segment in data
                # Include segment if it overlaps with our buffered window
                if (get_val(segment, 'start') + get_val(segment, 'duration')) >= buffered_start 
                and get_val(segment, 'start') <= buffered_end
            ]
            full_text = " ".join(filtered_segments)
            if not full_text.strip():
                print(f"[Transcript] No segments in time window, using full transcript")
                full_text = " ".join([get_val(segment, 'text') for segment in data])
            else:
                print(f"[Transcript] Found {len(filtered_segments)} segments in time window")
        else:
            full_text = " ".join([get_val(segment, 'text') for segment in data])
            print(f"[Transcript] Using full transcript: {len(data)} segments")
        
        print(f"[Transcript] ✅ Success: {len(full_text)} characters")
        return {"transcript": full_text}
        
    except Exception as e:
        error_msg = str(e)
        print(f"[Transcript] ❌ Error: {error_msg}")
        
        # If the api explicitly threw an exception saying it can't find a transcript, that is a 404, not a 500.
        if "Could not retrieve a transcript" in error_msg or "No transcripts were found" in error_msg or "disabled" in error_msg.lower():
            return JSONResponse(status_code=404, content={"error": "Transcript not found or disabled for this video."})
            
        return JSONResponse(status_code=500, content={"error": error_msg})
