# -*- coding: utf-8 -*-
import os
import sys
from src.sikulixWrapper import SikulixWrapper
from src.actionTypes import ActionType  

def load_graph(graph_file, img_dir):
 
    vertices = {}
    edges = []

    with open(graph_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if parts[0] == 'v' and len(parts) >= 3:
                name = parts[1]
                raw_path = " ".join(parts[2:]).strip('"')
                vertices[name] = os.path.join(img_dir, raw_path)
            elif parts[0] == 'e' and len(parts) >= 5:
                action_str = parts[1]
                src = parts[2]
                tgt = parts[3]
                raw_path = " ".join(parts[4:]).strip('"')

                try:
                    action = ActionType.from_string(action_str)
                except KeyError:
                    print("[ERROR] Unknown action "+ action_str +" in graph file.")
                    sys.exit(1)

                if action == ActionType.CLICK_AND_TYPE and len(parts) >= 6:
                    # Format: e CLICK_AND_TYPE Unity A C image.png
                    text_to_type = parts[2]
                    src = parts[3]
                    tgt = parts[4]
                    raw_path = " ".join(parts[5:]).strip('"')
                    edges.append((action, src, tgt, os.path.join(img_dir, raw_path), text_to_type))
                else:
                    # Format: e CLICK A B image.png
                    src = parts[2]
                    tgt = parts[3]
                    raw_path = " ".join(parts[4:]).strip('"')
                    edges.append((action, src, tgt, os.path.join(img_dir, raw_path), None))

    return vertices, edges


def main():
    cwd       = os.getcwd()
    img_dir   = os.path.join(cwd, "imgs")
    graph_txt = os.path.join(cwd, "graph.txt")
    sikuli = SikulixWrapper()
    vertices, edges = load_graph(graph_txt, img_dir)
    
    # check if vertices are defined
    if not vertices:
        print("[ERROR] No vertices found in graph.txt")
        sys.exit(1)

    if not edges:
        print("[INFO] No transitions defined — nothing to traverse")
        sys.exit(0)

    similarity = 1.0
    timeout    = 0.2

    for action,src, tgt, btn_path,text in edges:
        if src not in vertices: # Check if the source vertex is defined
            print("[ERROR] Source vertex '"+src+"' not defined")
            sys.exit(1)
        if tgt not in vertices:
            print("[ERROR] Target vertex '"+tgt+"' not defined")
            sys.exit(1)

        src_img = vertices[src]
        tgt_img = vertices[tgt]

      
        # 1) Wait for source node
        print("Waiting for node '"+src+"': "+src_img)
        if not sikuli.search_image(src_img, similarity, timeout):
            print("[ERROR] Node " + src + " not detected after some tries.")
            sikuli.capture_error("error_wait_"+src+".png", cwd)
            sys.exit(1)

        print("[OK] Node '"+src+"' detected")
        if action == ActionType.CLICK:
            # 2) Click the button for this edge
            print("Clicking button for edge "+src+" -> "+tgt+": "+btn_path)
            if sikuli.click_image(btn_path,similarity,timeout):
                print("[OK] Clicked button from '"+src+"' to '"+tgt+"'.")
            else:
                print("[ERROR] Button image for edge "+src+" -> "+tgt+" not found")
                sikuli.capture_error("error_button_"+src+"_"+tgt+".png", cwd)
                sys.exit(1)
        elif action == ActionType.CLICK_AND_TYPE:
            if sikuli.write_text(btn_path,text,similarity,timeout):
                print("[OK] Clicked button from '"+src+"' to '"+tgt+"'.")
            else:
                print("[ERROR] Button image for edge "+src+" -> "+tgt+" not found")
                sikuli.capture_error("error_button_"+src+"_"+tgt+".png", cwd)
                sys.exit(1)

        # 3) Verify that the target node appears
        print("Verifying node '"+tgt+"': "+tgt_img)
        if sikuli.search_image(tgt_img,similarity,timeout):
            print("[OK] Node '"+tgt+"' detected")
        else:
            print("[FAIL] Node '"+tgt+"' not found. Transition " + src + "->" +tgt)
            sikuli.capture_error("error_button_"+src+"_"+tgt+".png", cwd)
            sys.exit(1)
       
    print("[COMPLETE] All transitions completed successfully")
    sys.exit(0)

if __name__ == "__main__":
    main()
