"""Source-bound recipe builder. Requires a unique evidence run and explicit --publish.

See region_mask_pipeline.py --help and research/region-mask-workflow.md.
Original GLB and pin coordinates are never written.
"""
from region_mask_pipeline import main

if __name__ == '__main__':
    main()
