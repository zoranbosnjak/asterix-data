# asterix-data

XML description of ASTERIX data format as specified in
http://www.eurocontrol.int/services/asterix.
Each ASTERIX category and revision is specified in a separate `.xml` file.

**_NOTE:_** This projet is obsolete in favor of
https://github.com/zoranbosnjak/asterix-specs.
Instead of editing *.xml* files directly, please write new category
definitions in *.ast* format. For existing projects, it is still possible
to use *.xml* format by converting from *.ast* -> *.json* -> *.xml*.

# Conversion from .ast/.json to .xml

Use `nix` to build `asterix-specs` project. This includes building *.json* files out of *.ast* files.

```bash
nix-build -o asterix-specs https://github.com/zoranbosnjak/asterix-specs/archive/master.tar.gz
```

## Test on a single file

Render generated *.json* to *.xml* (single file)

```bash
./asterix-specs/bin/render --script render-json/xml.py render asterix-specs/specs/.../definition.json > xml/catABC_X.Y.xml
```

## Semi automatic procedure

```bash
./update-from-asterix-specs.py asterix-specs/ xml/
./update-from-asterix-specs.py asterix-specs/ xml/ | sh

git add xml

# review changes
git diff --cached

# commit with reference to asterix-specs revision
git commit -m "sync with asterix-specs <rev>"
```

# Install

* `scons` utility is used to run validation and installation (similar to `make`).
* `jing` application is used to optionally validate xml file against the template.

## Data validation

To validate XML (not strictly necessary), use

```bash
scons validate
```

## Installation

To install files to default location `/usr/local/share/asterix-data`, use

```bash
scons install
# or
sudo scons install
```

To install files to custom location, use for example

```bash
mkdir tmp
scons install --prefix=tmp
```

