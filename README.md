# fugashi-bundled

A bundled version of [fugashi](https://github.com/polm/fugashi)
created for the purposes of vendoring fugashi into an
[Anki](https://apps.ankiweb.net/) addon. Since Anki addons aren't
installed with a package manager, it becomes necessory to vendor in
dependencies, but fugashi both uses Cython and an external library
(mecab) so it becomes difficult to support all platforms and abi
versions Anki works with.

## Issues

You may notice there are no
[Releases](https://github.com/lambdadog/fugashi-bundled/releases)
yet. This is because [I don't currently have an Apple Developer
account](https://github.com/lambdadog/fugashi-bundled/issues/1), as
I'm short on funds, and therefore I can't sign my build of
`mecab.dylib` or the MacOS Cython builds of fugashi.pyx for each
supported ABI version.

The bundle published by CI should work flawlessly for Linux and
Windows, but on MacOS you will get popups saying that you can't run
files when you try to import the library. If you go into your System
Preferences and allow each file that fails to load (it will take two
tries and two files), the bundled fugashi will work properly, but
there's no way to get around this without signing or requiring users
to perform overly technical tasks.

## License and Copyright Notice

fugashi-bundled is, like fugashi, released under the terms of the [MIT
license](./LICENSE). Please copy it far and wide.

fugashi is a wrapper for MeCab, and the fugashi bundles include MeCab
binaries.  MeCab is copyrighted free software by Taku Kudo
`<taku@chasen.org>` and Nippon Telegraph and Telephone Corporation,
and is redistributed under the [BSD License](./LICENSE.mecab).
