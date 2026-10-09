# craft-update

Build, install and update the [ArtCraft](https://getartcraft.com/) Crafting Apps on Linux from
source, with launcher icons and an optional daily update timer.

The Crafting Apps are open-source, native desktop apps written in Rust. New changes land almost
every day. `craft-update` pulls each app's repo, rebuilds only the apps that changed, and installs
them for your user with their menu entries, icons and file types.

> **Unofficial.** This is a small community script. It is not made by or affiliated with ArtCraft
> or the Crafting Apps team. For the apps themselves, see
> [getartcraft.com/apps](https://getartcraft.com/apps), the
> [storytold GitHub organization](https://github.com/storytold), or the
> [ArtCraft Discord](https://discord.gg/artcraft).

## The Crafting Apps

| App | What it is |
|---|---|
| [PdfCraft](https://github.com/storytold/pdfcraft) | PDF reader and workbench (Acrobat-style) |
| [WordCraft](https://github.com/storytold/wordcraft) | Word processor (Word-style) |
| [GridCraft](https://github.com/storytold/gridcraft) | Spreadsheet (Excel-style) |
| [DeckCraft](https://github.com/storytold/deckcraft) | Presentations (PowerPoint-style) |
| [PhotoCraft](https://github.com/storytold/photocraft) | Image editor (Photoshop-style) |
| [LightCraft](https://github.com/storytold/lightcraft) | Photo library and editing (Lightroom-style) |
| [VectorCraft](https://github.com/storytold/vectorcraft) | Vector graphics (Illustrator-style) |
| [DesignCraft](https://github.com/storytold/designcraft) | Page layout (InDesign-style) |
| [CADCraft](https://github.com/storytold/cadcraft) | Drafting (AutoCAD-style) |
| [SoundCraft](https://github.com/storytold/soundcraft) | Audio editing and mixing (Pro Tools-style) |
| [FilmCraft](https://github.com/storytold/filmcraft) | Video editing (Premiere Pro-style) |
| [EffectCraft](https://github.com/storytold/effectcraft) | Motion graphics and compositing (After Effects-style) |

`craft-update` has been used with PdfCraft, PhotoCraft, DeckCraft, SoundCraft, FilmCraft, WordCraft
and GridCraft on Fedora 44 with GNOME. The other apps use the same repo layout, so they should
work too, but they haven't been tested yet.

## What it does

For each app in your list, `craft-update`:

1. Clones `github.com/storytold/<app>` into `~/git/<app>` if it isn't there, or pulls the latest
   `main` (fast-forward only).
2. Skips the build if the commit hasn't changed since the last successful build.
3. Runs `cargo build --release --locked -p <app>` at low CPU priority.
4. Links the binary into `~/.local/bin` and installs the app's `.desktop` file, MIME types and
   icons into `~/.local/share`, so the app shows up in your launcher.

If a build fails, the app you already have keeps working, and the next run tries again.

## Requirements

- `git` and a Rust toolchain (`cargo`). Your distribution's Rust packages work.
- The usual build headers for desktop apps. SoundCraft and FilmCraft also need ALSA:
  - Fedora: `sudo dnf install gcc pkgconf-pkg-config gtk3-devel alsa-lib-devel`
  - Debian/Ubuntu: `sudo apt install build-essential pkg-config libgtk-3-dev libasound2-dev`
- `~/.local/bin` on your `PATH`.
- Disk space: each app's build folder (`~/git/<app>/target`) takes a couple of GB. A build takes a
  few minutes per app.

## Install

```sh
git clone https://github.com/fqazzazee/craft-update ~/git/craft-update
~/git/craft-update/install.sh
craft-update
```

`install.sh` links `craft-update` into `~/.local/bin` and turns on the daily timer. Use
`./install.sh --no-timer` to skip the timer, or `./install.sh --uninstall` to remove both. Your apps
and their repos are never deleted.

The first `craft-update` run clones and builds every app in the list, which can take a while.

## Usage

```sh
craft-update                    # update every app; rebuild only the ones that changed
craft-update photocraft         # update just these apps
craft-update --force            # rebuild even if nothing changed
craft-update --list             # show each app's built commit and how many new commits are waiting
```

## Choosing apps

The app list is `~/.config/craft-update/apps`. It's created on the first run. Put one app per line,
optionally followed by extra `cargo build` flags:

```
pdfcraft
photocraft --features heif
gridcraft @x11
```

- To add an app, add its repo name and run `craft-update`. It's cloned and built for you.
- To stop updating an app, delete its line. Nothing is uninstalled.
- `--features heif` matches PhotoCraft's official builds, which can open HEIC/HEIF photos.
- `@x11` is explained below.

## Daily updates

The timer (`systemd/craft-update.timer`) runs `craft-update` once a day around 12:30 local time.
If your computer is off then, it runs the next time you log in. When something was updated or failed,
you get a desktop notification.

```sh
systemctl --user list-timers craft-update.timer     # when it runs next
journalctl --user -u craft-update.service           # what the last runs did
systemctl --user disable --now craft-update.timer   # turn it off
```

To change the time, edit `OnCalendar=` in `~/.config/systemd/user/craft-update.timer`, then run
`systemctl --user daemon-reload`.

## GNOME on Fedora: known issues and workarounds

These come from how the apps are built today, and are reported upstream.

**Title bar doesn't match GNOME.** On GNOME Wayland, the apps draw a plain title bar that ignores
your theme and dark mode. Add `@x11` after an app's name in the app list, and its launcher starts the
app through Xwayland instead. GNOME then draws its normal title bar. Remove `@x11` and run
`craft-update <app>` to switch back; nothing is rebuilt. PhotoCraft draws its own title bar, so it
doesn't need this. Reported in
[gridcraft#54](https://github.com/storytold/gridcraft/issues/54),
[pdfcraft#553](https://github.com/storytold/pdfcraft/issues/553),
[deckcraft#26](https://github.com/storytold/deckcraft/issues/26),
[filmcraft#433](https://github.com/storytold/filmcraft/issues/433),
[wordcraft#78](https://github.com/storytold/wordcraft/issues/78) and
[soundcraft#45](https://github.com/storytold/soundcraft/issues/45).

**Symbols show as empty boxes.** GridCraft and SoundCraft look for system fonts only in
Debian/Arch folders, so on Fedora they fall back to built-in fonts that lack arrows, check marks and
similar symbols. Install DejaVu Sans and link it where the apps look:

```sh
sudo dnf install dejavu-sans-fonts
sudo mkdir -p /usr/local/share/fonts
sudo ln -sfn /usr/share/fonts/dejavu-sans-fonts /usr/local/share/fonts/dejavu
```

The link makes DejaVu Sans appear twice in font pickers. To hide the copy, save this as
`~/.config/fontconfig/conf.d/90-craft-dejavu-link.conf`:

```xml
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">
<fontconfig>
  <selectfont>
    <rejectfont>
      <glob>/usr/local/share/fonts/dejavu/*</glob>
    </rejectfont>
  </selectfont>
</fontconfig>
```

PdfCraft only needs the `dejavu-sans-fonts` package. Reported in
[gridcraft#54](https://github.com/storytold/gridcraft/issues/54) and
[soundcraft#45](https://github.com/storytold/soundcraft/issues/45).

## Settings

| Variable | Default | Meaning |
|---|---|---|
| `CRAFT_SRC_DIR` | `~/git` | Where the app repos live |
| `CRAFT_UPDATE_NOTIFY` | unset (set by the timer) | Send a desktop notification after a run |

## License

Licensed under either of [Apache License, Version 2.0](LICENSE-APACHE) or [MIT license](LICENSE-MIT)
at your option, the same as the Crafting Apps.

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in
this project by you, as defined in the Apache-2.0 license, shall be dual licensed as above, without
any additional terms or conditions.
