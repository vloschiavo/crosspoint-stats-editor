import struct
import os
from pathlib import Path

def decode_global_stats(bin_path: str | Path):
    """
    Decode CrossInk / CrossPoint global_stats.bin file.
    """
    path = Path(bin_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    data = path.read_bytes()
    
    if len(data) < 1:
        raise ValueError("Empty file")
    
    version = data[0]
    print(f"Global Stats Version: {version}")
    print(f"File size: {len(data)} bytes")
    
    if version == 2:
        # Current format (as of the docs)
        if len(data) < 17:
            print("Warning: File too small for version 2")
            return None
        
        # [0]      version (= 2)
        # [1-4]    totalSessions       uint32 LE
        # [5-8]    totalReadingSeconds uint32 LE
        # [9-12]   totalPagesTurned    uint32 LE
        # [13-16]  completedBooks      uint32 LE
        
        total_sessions, total_seconds, total_pages, completed_books = struct.unpack_from(
            '<I I I I', data, 1
        )
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        print("\n=== Global Reading Statistics ===")
        print(f"Total reading sessions : {total_sessions:,}")
        print(f"Total reading time     : {total_seconds:,} seconds ({hours}h {minutes:02d}m {seconds:02d}s)")
        print(f"Total pages turned     : {total_pages:,}")
        print(f"Books marked completed : {completed_books:,}")
        
        # Average reading speed
        if total_pages > 0:
            avg_sec_per_page = total_seconds / total_pages
            print(f"Avg time per page      : {avg_sec_per_page:.1f} seconds")
        
    elif version == 1:
        # Older format (without completedBooks)
        if len(data) < 13:
            print("Warning: File too small for version 1")
            return None
            
        total_sessions, total_seconds, total_pages = struct.unpack_from('<I I I', data, 1)
        
        print("\n=== Global Reading Statistics (v1) ===")
        print(f"Total reading sessions : {total_sessions:,}")
        print(f"Total reading time     : {total_seconds:,} seconds")
        print(f"Total pages turned     : {total_pages:,}")
        print("Completed books        : (not tracked in v1)")
        
    else:
        print(f"Unknown version: {version}")
        print("Raw hex dump:")
        print(data.hex())
        return None
    
    return {
        'version': version,
        'total_sessions': total_sessions,
        'total_reading_seconds': total_seconds,
        'total_pages_turned': total_pages,
        'completed_books': completed_books if version >= 2 else 0
    }


# Example usage
if __name__ == "__main__":
    # Adjust path as needed
    stats_file = ".crosspoint/global_stats.bin"  # or full path
    if os.path.exists(stats_file):
        decode_global_stats(stats_file)
    else:
        print(f"File not found: {stats_file}")
        print("Make sure you're running this from the root of your SD card / mounted reader filesystem.")
