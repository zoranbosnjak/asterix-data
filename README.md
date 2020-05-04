# asterix-data

XML description of ASTERIX data format as specified in
http://www.eurocontrol.int/services/asterix.
Each ASTERIX category and revision is specified in a separate `.xml` file.

**_NOTE:_** This projet obsolete in favor of https://github.com/zoranbosnjak/asterix-specs.
Instead of editing *.xml* files directly, please write new category definitions in *.ast* format.
For existing projects, it is still possible to use *.xml* format by converting from *.ast* -> *.json* -> *.xml*.

# Conversion from .ast/.json to .xml

Use `nix` to build `asterix-specs` project. This includes building *.json* files out of *.ast* files.

```bash
cd /tmp
git clone https://github.com/zoranbosnjak/asterix-specs
cd asterix-specs
nix-build
```

Render generated *.json* to *.xml*.

```bash
cd <this_project>
/tmp/asterix-specs/result/bin/render --script render-json/xml.py render /tmp/asterix-specs/result/specs/catABC/vX.Y/cat<num>-v<ed>.json > xml/catABC_X.Y.xml
git add xml/catABC_X.Y.xml
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

