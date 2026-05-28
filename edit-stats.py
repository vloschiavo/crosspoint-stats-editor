#!/usr/bin/env python3
import struct
import os
import shutil
from pathlib import Path
from datetime import timedelta

def decode_global_stats(bin_path: str | Path, show=True):
    """Decode and optionally display the global_stats.bin file."""
    path = Path(bin_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    data = path.read_bytes()
    if len(data) < 1:
        raise ValueError("Empty file")
    
    version = data[0]
    
    if version == 2:
        if len(data) < 17:
            raise ValueError("File too small for version 2")
        
        total_sessions, total_seconds, total_pages, completed_books = struct.unpack_from(
            '<I I I I', data, 1
        )
        
        if show:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            
            print("\n=== Global Reading Statistics ===")
            print(f"Version                : {version}")
            print(f"Total reading sessions : {total_sessions:,}")
            print(f"Total reading time     : {total_seconds:,} seconds ({hours}h {minutes:02d}m {seconds:02d}s)")
            print(f"Total pages turned     : {total_pages:,}")
            print(f"Books marked completed : {completed_books:,}")
            
            if total_pages > 0:
                print(f"Avg time per page      : {total_seconds / total_pages:.1f} seconds")
    
    elif version == 1:
        if len(data) < 13:
            raise ValueError("File too small for version 1")
        total_sessions, total_seconds, total_pages = struct.unpack_from('<I I I', data, 1)
        completed_books = 0
        if show:
            print("\n=== Global Reading Statistics (v1 - older) ===")
            print(f"Total reading sessions : {total_sessions:,}")
            print(f"Total reading time     : {total_seconds:,} seconds")
            print(f"Total pages turned     : {total_pages:,}")
            print(f"Completed books        : (not tracked)")
    else:
        print(f"Unknown version: {version}")
        return None
    
    return {
        'version': version,
        'total_sessions': total_sessions,
        'total_reading_seconds': total_seconds,
        'total_pages_turned': total_pages,
        'completed_books': completed_books
    }


def edit_global_stats(bin_path: str | Path, 
                      sessions: int = None,
                      seconds: int = None,
                      pages: int = None,
                      completed: int = None):
    """
    Edit values in global_stats.bin and write back.
    Only provided values will be changed.
    """
    path = Path(bin_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    # Create backup
    backup_path = path.with_suffix('.bin.bak')
    shutil.copy2(path, backup_path)
    print(f"Backup created: {backup_path}")

    stats = decode_global_stats(path, show=False)

    version = stats['version']
    
    # Update values if provided
    if sessions is not None:
        stats['total_sessions'] = max(0, int(sessions))
    if seconds is not None:
        stats['total_reading_seconds'] = max(0, int(seconds))
    if pages is not None:
        stats['total_pages_turned'] = max(0, int(pages))
    if completed is not None:
        stats['completed_books'] = max(0, int(completed))

    # Rebuild binary
    if version == 2:
        new_data = struct.pack(
            '<B I I I I',
            version,
            stats['total_sessions'],
            stats['total_reading_seconds'],
            stats['total_pages_turned'],
            stats['completed_books']
        )
    elif version == 1:
        new_data = struct.pack(
            '<B I I I',
            version,
            stats['total_sessions'],
            stats['total_reading_seconds'],
            stats['total_pages_turned']
        )
    else:
        raise ValueError(f"Unsupported version: {version}")

    # Write back
    path.write_bytes(new_data)
    print("✅ Successfully updated global_stats.bin")

    # Show updated values
    decode_global_stats(path, show=True)


# ====================== Interactive Mode ======================
if __name__ == "__main__":
    stats_file = ".crosspoint/global_stats.bin"   # Change if needed

    if not os.path.exists(stats_file):
        print(f"❌ File not found: {stats_file}")
        print("Please run this script from the root of your e-reader's storage.")
    else:
        print("Current values:")
        decode_global_stats(stats_file)

        print("\n" + "="*50)
        print("Edit Global Stats")
        print("="*50)
        
        try:
            sessions = input("Total reading sessions (Enter to keep current): ").strip()
            seconds = input("Total reading time in seconds: ").strip()
            pages = input("Total pages turned: ").strip()
            completed = input("Completed books: ").strip()

            edit_global_stats(
                stats_file,
                sessions=int(sessions) if sessions else None,
                seconds=int(seconds) if seconds else None,
                pages=int(pages) if pages else None,
                completed=int(completed) if completed else None
            )
        except ValueError:
            print("❌ Invalid input. Please enter numbers only.")
        except Exception as e:
            print(f"❌ Error: {e}")
