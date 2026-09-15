# Number of containers to run in parallel.
MAX_CONTAINER_NUM = 9

# Memory limitation (in GB) for each container.
MEM_PER_CONTAINER = 1

# Each line represents <program, seed format, cmdline argument, input file>
TARGETS = [
    ("objdump","elf", "-D input", "input"),
    ("strip","elf", "input -o /tmp/trash", "input"),
    ("readelf","elf", "-h -l -S -s input", "input"),
    ("tiff_read_rgba_fuzzer","tiff", "input.tif", "input.tif"),
    ("libpng_read_fuzzer","png","input.png", "input.png"),
    ("exiv2", "jpeg-exif", "input.jpg", "input.jpg"),
    ("idlc", "idl", "input.idl", "input.idl"),
    ("pdftotext","pdf","input.pdf 1", "input.pdf"),
    ("nasm", "asm", "-f elf64 -o /tmp/out.o input.asm", "input.asm"),
]
