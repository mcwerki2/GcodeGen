# By Werki 13.01.2024
import json
import os.path

info_tabelle = {"+X_+Y": "X_Y-_X-_Y",
                "+X_-Y": "X_Y_X-_Y-",
                "-X_+Y": "X-_Y-_X_Y",
                "-X_-Y": "X-_Y_X_Y-",
                "+Y_+X": "Y_X-_Y-_X",
                "+Y_-X": "Y_X_Y-_X-",
                "-Y_+X": "Y-_X-_Y_X",
                "-Y_-X": "Y-_X_Y_X-"}

# TODO: Werkzeugradius korrektur


def get_user_input():
    """Bekommt die Inputs des Benutzers"""
    if input("Test (y/n)?: ").lower() == "y":
        with open("test.json", "r") as f:
            output_user = json.load(f)

    else:
        vorschub_ges = int(input("Vorschub (mm/min): "))
        zustellung = float(input("Zustellung (mm): "))
        schnitt_tiefe = int(input("Tiefe des Schnitts (mm): "))
        # werkzeug_radius = int(input("Fräser Radius (mm): "))
        len_des_schnitts = int(input("Länge des Schnitts (mm): "))
        x_position_schnitt_anfang = int(input("X Position Schnitt Anfang (mm): "))
        y_position_schnitt_anfang = int(input("Y Position Schnitt Anfang (mm): "))
        z_position_schnitt_anfang = int(input("z Position Schnitt Anfang (mm): "))
        richtung_des_schnitts = input("Richtung des Schnitts (+X, -X, +Y, -Y): ").upper()
        lage_des_materials = input("Lage des Materials (+X, -Y, +Y, -Y): ").upper()
        datei_name = input("Dateiname(str): ").replace(" ", "")
        sicherheitsabstand = int(input("sicherheitsabstand (größer als fräser radius) (mm): "))
        output_user: dict = {"vorschub_ges": vorschub_ges, "zustellung": zustellung, "schnitt_tiefe": schnitt_tiefe, "len_des_schnitts": len_des_schnitts, "x_position_schnitt_anfang": x_position_schnitt_anfang,
                             "y_position_schnitt_anfang": y_position_schnitt_anfang, "z_position_schnitt_anfang": z_position_schnitt_anfang, "richtung_des_schnitts": richtung_des_schnitts, "lage_des_materials": lage_des_materials, "datei_name": datei_name, "sicherheitsabstand": sicherheitsabstand} # NOQA
        print("\n\n")
    return output_user


def write_file(name, cont):
    if os.path.isfile(f"./{name}.nc"):
        print("Datei existiert! nicht geschrieben")
        if input("Trotzdem schreiben (y/n)?: ").lower() == "n":
            return
        else:
            with open(f"{name}.nc", "w") as f: # NOQA
                pass
            with open(f"{name}.nc", "a") as f:
                for i in cont:
                    f.write(i)
            print("erfolgreich geschrieben")
    else:
        with open(f"{name}.nc", "a") as f:
            for i in cont:
                f.write(i)
                f.write("\n")
        print("erfolgreich geschrieben")


def cut_para(input_user, info_liste):
    list_search = f"{input_user['richtung_des_schnitts']}_{input_user['lage_des_materials']}"
    result = info_liste[list_search].split("_")
    return result


def cycle_define(input_user, info_liste):
    output: list[str] = []
    len_des_schnitts = input_user["len_des_schnitts"] + input_user["sicherheitsabstand"] + input_user["sicherheitsabstand"] + input_user["zustellung"]
    
    for key, value in input_user.items():
        output.append(f"(Einstellung: {key} = {value})")
    output.append("\n\nG90 (Absolute Positionierung)\n")
    output.append(f"G0 X{input_user['x_position_schnitt_anfang'] - input_user['sicherheitsabstand'] - input_user['zustellung']} Y{input_user['y_position_schnitt_anfang'] - input_user['sicherheitsabstand'] - input_user['zustellung']} Z{input_user['z_position_schnitt_anfang']}") # NOQA

    output.append(f"\nG91 (Relative Positionierung)\n")

    # Eigentliche Logik

    para_list = cut_para(input_user, info_liste)
    passes, rest = divmod(input_user["schnitt_tiefe"], input_user["zustellung"])
    while passes != 0:
        output.append(f"G1 {para_list[3]}{input_user['sicherheitsabstand'] + input_user['zustellung']} F{input_user['vorschub_ges']}")
        output.append(f"G1 {para_list[0]}{len_des_schnitts} F{input_user['vorschub_ges']}")
        output.append(f"G0 {para_list[1]}{input_user['sicherheitsabstand']}")
        output.append(f"G0 {para_list[2]}{len_des_schnitts}\n")
        passes -= 1

    output.append(f"G1 {para_list[3]}{input_user['sicherheitsabstand'] + rest} F{input_user['vorschub_ges']}")
    output.append(f"G1 {para_list[0]}{len_des_schnitts} F{input_user['vorschub_ges']}")
    output.append(f"G0 {para_list[1]}{input_user['sicherheitsabstand']}")
    output.append(f"G0 {para_list[2]}{len_des_schnitts}\n")
    output.append(f"\nM30\n")

    print("\n")
    print("[Output]:")
    for i in output:
        print(f"{i}")
    return output


temp1 = get_user_input()
temp2 = cycle_define(temp1, info_tabelle)
write_file(temp1["datei_name"], temp2)
