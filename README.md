# Talk to Me

A fun project that uses the Piper project to generate
audiobooks from EPUC files

## What

Run script and pass one or more paths to EPUB files on your
machine.

## How

Build the project using the included script. You must have `podman`  
installed on your real system.
```bash
$ ./bin/dockerize
```

Run the project with `podman` or use the convenience script included:
```bash
$ ./bin/ttm /path/to/my/book.epub /path/to/another/book.epub
```

See what happens!

## License

Apache 2

```
Copyright 2023 pyamsoft

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
