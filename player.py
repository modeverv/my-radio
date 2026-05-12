import subprocess

def search_and_play(query: str) -> bool:
    # Escape double quotes and remove characters that might break search
    clean_query = query.replace('"', '\\"').split('(')[0].split('[')[0].strip()
    
    script = f'''
    tell application "Music"
        -- Search in the main library playlist (playlist 1 is usually "Library" or "Music")
        set results to search playlist 1 for "{clean_query}"
        if results is not {{}} then
            play item 1 of results
            return true
        else
            return false
        end if
    end tell
    '''
    
    try:
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        is_success = result.stdout.strip() == "true"
        if not is_success:
            print(f"[player] 曲が見つかりません: {clean_query} (Original: {query})")
        return is_success
    except Exception as e:
        print(f"[player] Error during search_and_play: {e}")
        return False

def get_now_playing() -> dict:
    script = '''
    tell application "Music"
        if player state is playing then
            set t to name of current track
            set a to artist of current track
            set d to duration of current track
            return t & "||" & a & "||" & (d as string)
        else
            return "not_playing"
        end if
    end tell
    '''
    
    fallback = {"title": "Unknown", "artist": "Unknown", "duration": 30.0}
    
    try:
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        output = result.stdout.strip()
        
        if output == "not_playing" or not output:
            return fallback
            
        parts = output.split("||")
        if len(parts) == 3:
            return {
                "title": parts[0],
                "artist": parts[1],
                "duration": float(parts[2])
            }
        return fallback
    except Exception as e:
        print(f"[player] Error during get_now_playing: {e}")
        return fallback

if __name__ == "__main__":
    # Test: Get currently playing track
    print(f"Now playing: {get_now_playing()}")
    
    # Test: Search for a track (example)
    # search_and_play("Beatles")
