import argparse
import json
import os
import sys
import logging
import time
import jsonschema

def main():
    # 1. Parse command-line arguments
    parser = argparse.ArgumentParser(description="JSON Patching Tool")
    parser.add_argument("-new", type=str, help="Path to the new JSON file", required=True)
    parser.add_argument("-old", type=str, help="Path to the old JSON file", required=True)
    parser.add_argument("-debug", action="store_true", help="Enable debug mode (no file writing)")
    parser.add_argument("-lang", type=str, default="en-us", help="Localization language code (default: en-us)")
    args = parser.parse_args()

    # 2. Set up logging
    log_time = time.strftime("%Y-%m-%d-%H%M%S")
    log_file = f"{log_time}_log.txt"
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s][%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.info("Log file created: {log_file}".format(log_file=log_file))

    # 3. Load localization file (JSON format)
    lang_file = f"{args.lang}.json"
    translations = {}
    if os.path.exists(lang_file):
        try:
            with open(lang_file, "r", encoding="utf-8") as f:
                translations = json.load(f)
            logging.info("Loaded language file: {lang_file}".format(lang_file=lang_file))
        except json.JSONDecodeError:
            logging.error("Language file {lang_file} has invalid format, using default language.".format(lang_file=lang_file))
    else:
        logging.warning("Language file '{lang_file}' not found, using default language.".format(lang_file=lang_file))

    def _(text):
        return translations.get(text, text)

    # 4. Load JSON file
    def load_json(file_path):
        if not os.path.exists(file_path):
            logging.error(_("{0} not found.").format(file_path))
            sys.exit(1)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logging.error(_("{0} cannot be read as a JSON file. Please check the format.").format(file_path))
            sys.exit(1)

    new_data = load_json(args.new)
    old_data = load_json(args.old)

    # 5. Identify JSON type using Schema
    schema_dir = "Schema"
    schemas = {
        "UnityDefaultFont_Ext": os.path.join(schema_dir, "UnityDefaultFont_Ext.json"),
        "TextMeshPro_MonoBehavior": os.path.join(schema_dir, "TextMeshPro_MonoBehavior.json"),
        "NGUI_MonoBehavior": os.path.join(schema_dir, "NGUI_MonoBehavior.json"),
        "NGUI_Sprite_MonoBehavior": os.path.join(schema_dir, "NGUI_Sprite_MonoBehavior.json"),
    }

    def has_minimum_structure(json_data, schema):
        """
        Check whether json_data contains at least all properties defined in the schema.
        Recursively checks nested properties.
        """
        if "properties" not in schema:
            return True
        for key, subschema in schema["properties"].items():
            if key not in json_data:
                return False
            if isinstance(json_data[key], dict) and "properties" in subschema:
                if not has_minimum_structure(json_data[key], subschema):
                    return False
        return True

    def identify_json_type(json_data):
        for schema_name, schema_path in schemas.items():
            if os.path.exists(schema_path):
                with open(schema_path, "r", encoding="utf-8") as f:
                    schema = json.load(f)
                try:
                    jsonschema.validate(instance=json_data, schema=schema)
                    if has_minimum_structure(json_data, schema):
                        return schema_name
                except jsonschema.exceptions.ValidationError:
                    continue
        return None

    new_type = identify_json_type(new_data)
    old_type = identify_json_type(old_data)

    if not new_type:
        logging.error(_("{0} has an unknown file type. Program terminated.").format(args.new))
        sys.exit(1)
    if not old_type:
        logging.error(_("{0} has an unknown file type. Program terminated.").format(args.old))
        sys.exit(1)

    if new_type != old_type:
        logging.error(_("{0} ({1}) and {2} ({3}) are of different types. Program terminated.").format(args.old, old_type, args.new, new_type))
        sys.exit(1)
    logging.info(_("{0} is of type {1}.").format(args.old, old_type))

    # 6. Compare keys
    new_keys = set(new_data.keys())
    old_keys = set(old_data.keys())

    extra_keys_in_new = new_keys - old_keys
    extra_keys_in_old = old_keys - new_keys

    if extra_keys_in_new:
        logging.warning(_("{0} contains keys that are not present in {1}: {2}").format(args.new, args.old, extra_keys_in_new))
        confirm = input(_("These keys will be discarded. Confirm? [Y/N]:"))
        if confirm.lower() != "y":
            logging.warning(_("User aborted the operation."))
            sys.exit(1)
        logging.info(_("User confirmed the operation."))

    if extra_keys_in_old:
        logging.warning(_("{0} contains keys that are not present in {1}: {2}").format(args.old, args.new, extra_keys_in_old))
        logging.error(_("Please adjust the new file to include the missing keys. Program terminated."))
        sys.exit(1)

    # 7. Define a function to update keys (supports nested key replacement)
    def update_keys(old_dict, new_dict, keys_mapping):
        for key, subkeys in keys_mapping.items():
            if key in old_dict and key in new_dict:
                if subkeys is None:
                    old_dict[key] = new_dict[key]
                    logging.info(_("{0} from the new file has been applied to the old file.").format(key))
                else:
                    # For partial updates of nested dictionaries
                    if isinstance(old_dict[key], dict) and isinstance(new_dict[key], dict):
                        for subkey in subkeys:
                            if subkey in old_dict[key] and subkey in new_dict[key]:
                                old_dict[key][subkey] = new_dict[key][subkey]
                                logging.info(_("{0}.{1} from the new file has been applied to the old file.").format(key, subkey))
                            else:
                                logging.warning(_("{0}.{1} does not exist in one of the files; not updated.").format(key, subkey))
                    else:
                        old_dict[key] = new_dict[key]
                        logging.info(_("Due to type mismatch, {0} has been fully replaced.").format(key))
            else:
                logging.warning(_("{0} does not exist in both files; no replacement made.").format(key))

    # 7. Define replacement rules based on file type
    replacement_keys = {
        "UnityDefaultFont_Ext": {
            "m_CharacterRects": None,
            "m_KerningValues": None,
            "m_PixelScale": None,
            "m_FontData": None,
        },
        "TextMeshPro_MonoBehavior": {
            "m_fontInfo": ["PointSize", "Scale", "CharacterCount", "LineHeight", "Baseline",
                           "Ascender", "CapHeight", "Descender", "CenterLine", "SuperscriptOffset",
                           "SubscriptOffset", "SubSize", "Underline", "UnderlineThickness", "strikethrough",
                           "strikethroughThickness", "TabWidth", "Padding", "AtlasWidth", "AtlasHeight"],
            "m_glyphInfoList": None,
            "m_kerningInfo": None,
            "m_kerningPair": None,
            "normalStyle": None,
            "normalSpacingOffset": None,
            "boldStyle": None,
            "boldSpacing": None,
            "italicStyle": None,
            "tabSize": None,
        },
        "NGUI_MonoBehavior": {
            "mUVRect": None,
            "mFont": None,
        },
        "NGUI_Sprite_MonoBehavior": {
            "mSprites": None,
            "mPixelSize": None,
        },
    }

    if old_type in replacement_keys:
        update_keys(old_data, new_data, replacement_keys[old_type])
    else:
        logging.warning(_("No replacement rules defined for type {0}.").format(old_type))

    # 8. Generate patched file
    patched_file = args.old.replace(".json", "_patched.json")
    if not args.debug:
        with open(patched_file, "w", encoding="utf-8") as f:
            json.dump(old_data, f, indent=4, ensure_ascii=False)
        logging.info(_("{0} patched file generated.").format(patched_file))
    else:
        logging.info(_("Debug mode enabled; no changes were written."))

    input(_("Press any key to exit."))

if __name__ == "__main__":
    main()
