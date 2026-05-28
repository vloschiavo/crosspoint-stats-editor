#!/usr/bin/env python3
import argparse
import struct
import shutil
import sys
from pathlib import Path
from datetime import timedelta

def decode_global_stats(bin_path: Path, show: bool = True):
    """Decode and display global_stats.bin"""
    if not bin_path.exists():
        print(f"❌ File not found: {bin_path}")
        return None

    data = bin_path.read_bytes()
    if len(data) < 1:
        print("❌ Empty file")
        return None

    version = data[0]

    if version == 2:
        if len(data) < 17:
            print("❌ File too small for version 2")
            return None
        total_sessions, total_seconds, total_pages, completed_books = struct.unpack_from(
            '<I I I I', data, 1
        )
        if show:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            print(f"\n=== Global Reading Statistics (v{version}) ===")
            print(f"File                   : {bin_path}")
            print(f"Total sessions         : {total_sessions:,}")
            print(f"Total reading time     : {total_seconds:,} seconds ({hours}h {minutes:02d}m {seconds:02d}s)")
            print(f"Total pages turned     : {total_pages:,}")
            print(f"Completed books        : {completed_books:,}")
            if total_pages > 0:
                print(f"Avg seconds per page   : {total_seconds / total_pages:.1f}")

    elif version == 1:
        if len(data) < 13:
            print("❌ File too small for version 1")
            return None
        total_sessions, total_seconds, total_pages = struct.unpack_from('<I I I', data, 1)
        completed_books = 0
        if show:
            print(f"\n=== Global Reading Statistics (v{version} - older) ===")
            print(f"File                   : {bin_path}")
            print(f"Total sessions         : {total_sessions:,}")
            print(f"Total reading time     : {total_seconds:,} seconds")
            print(f"Total pages turned     : {total_pages:,}")
            print(f"Completed books        : (not tracked in v1)")
    else:
        print(f"❌ Unknown version: {version}")
        return None

    return {
        'version': version,
        'total_sessions': total_sessions,
        'total_reading_seconds': total_seconds,
        'total_pages_turned': total_pages,
        'completed_books': completed_books
    }


def edit_global_stats(bin_path: Path, sessions=None, seconds=None, pages=None, completed=None):
    """Edit the stats file with provided values"""
    stats = decode_global_stats(bin_path, show=False)
    if stats is None:
        return

    # Create backup
    backup = bin_path.with_suffix('.bin.bak')
    shutil.copy2(bin_path, backup)
    print(f"✅ Backup created: {backup}")

    # Update values
    if sessions is not None:
        stats['total_sessions'] = max(0, sessions)
    if seconds is not None:
        stats['total_reading_seconds'] = max(0, seconds)
    if pages is not None:
        stats['total_pages_turned'] = max(0, pages)
    if completed is not None:
        stats['completed_books'] = max(0, completed)

    version = stats['version']

    # Pack new data
    if version == 2:
        new_data = struct.pack('<B I I I I',
            version,
            stats['total_sessions'],
            stats['total_reading_seconds'],
            stats['total_pages_turned'],
            stats['completed_books']
        )
    else:  # version 1
        new_data = struct.pack('<B I I I',
            version,
            stats['total_sessions'],
            stats['total_reading_seconds'],
            stats['total_pages_turned']
        )

    bin_path.write_bytes(new_data)
    print("✅ global_stats.bin successfully updated!")

    # Show updated values
    decode_global_stats(bin_path, show=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="CrossInk / CrossPoint global_stats.bin editor",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument('--file', '-f',
                        default='.crosspoint/global_stats.bin',
                        help='Path to global_stats.bin file')
    
    parser.add_argument('--sessions', '-s', type=int,
                        help='Set total reading sessions')
    
    parser.add_argument('--seconds', '-t', type=int,
                        help='Set total reading time in seconds')
    
    parser.add_argument('--pages', '-p', type=int,
                        help='Set total pages turned')
    
    parser.add_argument('--completed', '-c', type=int,
                        help='Set number of completed books')
    
    parser.add_argument('--view', '-v', action='store_true',
                        help='Only view current stats (no editing)')

    args = parser.parse_args()

    file_path = Path(args.file)

    if args.view:
        decode_global_stats(file_path)
    elif any([args.sessions, args.seconds, args.pages, args.completed]):
        edit_global_stats(
            file_path,
            sessions=args.sessions,
            seconds=args.seconds,
            pages=args.pages,
            completed=args.completed
        )
    else:
        print("ℹ️  No changes specified. Showing current stats:")
        decode_global_stats(file_path)

    print("\nDone.")
