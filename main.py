# By Werki 13.01.2024
import json
import os.path
import math
import numpy as np

info_tabelle = {"+X_+Y": "X_Y-_X-_Y",  # Eine Tabelle die der code benötigt, um Richtungen herauszufinden
                "+X_-Y": "X_Y_X-_Y-",
                "-X_+Y": "X-_Y-_X_Y",
                "-X_-Y": "X-_Y_X_Y-",
                "+Y_+X": "Y_X-_Y-_X",
                "+Y_-X": "Y_X_Y-_X-",
                "-Y_+X": "Y-_X-_Y_X",
                "-Y_-X": "Y-_X_Y_X-"}

# TODO: Werkzeugradius korrektur


def get_user_input():
    """Erfragt die eingaben des Benutzers"""
    input_temp = input("Test Lauf mit vorgegebenen parametern (j/n)?: ").lower()
    if input_temp == "j" or input_temp == "y":
        with open("test.json", "r") as f:
            output_user = json.load(f)

    else:
        freaser_radius = float(input("Fräser Radius (mm): "))
        vorschub_ges = int(input("Vorschub (mm/min): "))
        zustellung = float(input("Zustellung (mm): "))
        schnitt_radius = int(input("Tiefe des Schnitts (mm): "))
        spindel_ges = int(input("Spindel geschwindigkeit (rpm): "))
        len_des_schnitts = int(input("Länge des Schnitts (mm): "))
        x_position_schnitt_anfang = int(input("X Position Schnitt Anfang (mm): "))
        y_position_schnitt_anfang = int(input("Y Position Schnitt Anfang (mm): "))
        z_position_schnitt_anfang = int(input("z Position Schnitt Anfang (mm): "))
        richtung_des_schnitts = input("Richtung des Schnitts (+X, -X, +Y, -Y): ").upper()
        while richtung_des_schnitts not in ["+X", "-X", "+Y", "-Y"]:
            print("Falsche Eingabe!")
            richtung_des_schnitts = input("Richtung des Schnitts (+X, -X, +Y, -Y): ").upper()

        if richtung_des_schnitts == "+X" or richtung_des_schnitts == "-X":
            lage_des_materials = input("Lage des Materials (+Y, -Y): ").upper()
        else:
            lage_des_materials = input("Lage des Materials (+X, -X").upper()
        datei_name = input("Dateiname(str): ").replace(" ", "")
        sicherheitsabstand = int(input("sicherheitsabstand (größer als fräser radius) (mm): "))
        output_user: dict = {"freaser_radius": freaser_radius, "vorschub_ges": vorschub_ges, "zustellung": zustellung, "schnitt_raduis": schnitt_radius, "spindel_ges": spindel_ges, "len_des_schnitts": len_des_schnitts,
                             "x_position_schnitt_anfang": x_position_schnitt_anfang, "y_position_schnitt_anfang": y_position_schnitt_anfang, "z_position_schnitt_anfang": z_position_schnitt_anfang,
                             "richtung_des_schnitts": richtung_des_schnitts, "lage_des_materials": lage_des_materials, "datei_name": datei_name, "sicherheitsabstand": sicherheitsabstand} # NOQA
        print("\n\n")
    return output_user


def write_file(name, cont):
    """Schreibt den fertigen Gcode in eine datei."""

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
                    f.write("\n")
            print("erfolgreich geschrieben")
    else:
        with open(f"{name}.nc", "a") as f:
            for i in cont:
                f.write(i)
                f.write("\n")
        print("erfolgreich geschrieben")


def cut_para(input_user, info_liste):
    """Benutzt die eingaben des Benutzers mithilfe einer liste, um herauszufinden,
    in welcher seite weggestellt werden kann"""

    list_search = f"{input_user['richtung_des_schnitts']}_{input_user['lage_des_materials']}"
    result = info_liste[list_search].split("_")
    return result


def point_gen(degree_list, radius, dx, dz): # NOQA
    out: list = []
    for grad in degree_list:
        y_tmp: float = math.sin(grad) * radius
        x_tmp: float = math.cos(grad) * radius
        out.append((round(x_tmp, 4), round(y_tmp, 4)))
    shifted_points = [(x + dx, y + dz) for x, y in out]
    print(f"Ausgabe punkte liste: {out}")
    return out, shifted_points


def angle_gen(distance, radius): # NOQA
    out = []
    umfang = 2 * math.pi * radius
    anzahl_punkte = int(umfang / distance)
    print(f"Anzahl punkte: {anzahl_punkte}")
    kreisbogen = umfang / anzahl_punkte
    winkel = (180 * kreisbogen) / (radius * math.pi)
    winkel_liste = np.linspace(math.radians(0), math.radians(90), anzahl_punkte)
    for i in winkel_liste:
        out.append(round(i, 4))
    print(f"Winkel Liste: {out}")
    return out


def toolpath_gen(input_user, info_liste, points_list):
    output: list = []
    para_list = cut_para(input_user, info_liste)

    len_des_schnitts = input_user["len_des_schnitts"] + input_user["sicherheitsabstand"] + input_user["sicherheitsabstand"] + input_user["zustellung"]

    for point in points_list:
        output.append(f"G0 {para_list[0]}{len_des_schnitts}(3)")  # Schnitt
        output.append(f"G0 {para_list[1]}{input_user['sicherheitsabstand']}(1)")  # retract
        output.append(f"G1 {para_list[2]}{len_des_schnitts} F{input_user['vorschub_ges']}(2)\n") # zum anfang fahren
        output.append(f"G90")
        output.append(f"G0 {para_list[3]}{point[0]} Z{point[1]}(4)")  # Zustellung zum nächsten punkt
        output.append(f"G91")

    return output


def cycle_define(input_user, info_liste, points_list, toolpath_gcode):
    """Schreibt den Gcode in eine liste und gib dies zurück"""

    output: list[str] = []
    len_des_schnitts = input_user["len_des_schnitts"] + input_user["sicherheitsabstand"] + input_user["sicherheitsabstand"] + input_user["zustellung"]

    for key, value in input_user.items():
        output.append(f"(Einstellung: {key} = {value})")
    output.append("\n\nG90 (Absolute Positionierung)\n")
    output.append(f"G0 X{input_user['x_position_schnitt_anfang'] - input_user['sicherheitsabstand'] - input_user['zustellung']} Y{input_user['y_position_schnitt_anfang'] - input_user['sicherheitsabstand'] - input_user['zustellung']} Z{input_user['z_position_schnitt_anfang']}") # NOQA

    #  output.append(f"\nG91 (Relative Positionierung)\n")
    output.append(f"M03 S{input_user['spindel_ges']}")

    for i in toolpath_gcode:
        output.append(i)

    output.append(f"\nM05")
    output.append(f"\nM30\n")

    print("\n")
    print("[Output]:")
    for i in output:
        print(f"{i}")
    return output


if __name__ == '__main__':
    temp1 = get_user_input()
    # try:
    radius = 3
    angle_list = angle_gen(1, radius)
    points, sh = point_gen(angle_list, radius, 0, 0)
    temp2 = cycle_define(temp1, info_tabelle, points, toolpath_gen(temp1, info_tabelle, points))
    # except KeyError as err:
    #     print("Falsche eingabe werte.")
    #     print(err)
    #     print('{}: {}'.format(type(err).__name__, err))
    #     quit()
    write_file(temp1["datei_name"], temp2)
