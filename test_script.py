# -*- coding: utf-8 -*-
import os
import sys
from sikuli import Screen, Pattern

def load_graph(graph_file, img_dir):
    vertices = {}
    edges = []
    with open(graph_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):# skip empty lines or comments
                continue
            parts = line.split()
            if parts[0] == 'v' and len(parts) >= 3: # vertex definition
                name = parts[1]
                raw_path = " ".join(parts[2:]).strip('"')# image path
                vertices[name] = os.path.join(img_dir, raw_path)
            elif parts[0] == 'e' and len(parts) >= 4: # edge definition
                src = parts[1]
                tgt = parts[2]
                raw_path = " ".join(parts[3:]).strip('"')
                edges.append((src, tgt, os.path.join(img_dir, raw_path)))
    return vertices, edges

def search_image(screen, image_path, similarity=0.9, timeout=10, retries=3, similarity_reduction = 0.1 ):
    for attempt in range(retries):
        actual_attempt = attempt + 1
        actual_similarity = similarity - (similarity_reduction*attempt)
        print("Attempts " + str(actual_attempt) + "/" + str(retries))
        match = screen.exists(Pattern(image_path).similar(actual_similarity), timeout)
        if match:
            print("[OK] Image found.")
            return True
        else:
            print("[WARNING] Not found. Trying again...")

    return False

def click_image(screen, image_path, similarity=0.9, timeout=10, retries=3, similarity_reduction = 0.1 ):
    for attempt in range(retries):
        actual_attempt = attempt + 1
        actual_similarity = similarity - (similarity_reduction*attempt)
        print("Attempts " + str(actual_attempt) + "/" + str(retries))
        match = screen.exists(Pattern(image_path).similar(actual_similarity), timeout)
        if match:
            screen.click(Pattern(image_path).similar(actual_similarity))
            print("[OK] Clicked image.")
            return True
        else:
            print("[WARNING] Not found. Trying again...")

    return False

def main():
    cwd       = os.getcwd()
    img_dir   = os.path.join(cwd, "imgs")
    graph_txt = os.path.join(cwd, "graph.txt")

    vertices, edges = load_graph(graph_txt, img_dir)
    
    # check if vertices are defined
    if not vertices:
        print("[ERROR] No vertices found in graph.txt")
        sys.exit(1)

    if not edges:
        print("[INFO] No transitions defined — nothing to traverse")
        sys.exit(0)

    screen     = Screen()
    similarity = 0.7
    timeout    = 2

    for src, tgt, btn_path in edges:
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
        if not search_image(screen, src_img, similarity, timeout):
            print("[ERROR] Node "+src+ "not detected after some tries.")
            screen.capture().save(cwd,"error_wait_"+{src}+".png")
            sys.exit(1)

        print("[OK] Node '"+src+"' detected")

        # 2) Click the button for this edge
        print("Clicking button for edge "+src+" -> "+tgt+": "+btn_path)
        if click_image(screen,btn_path,similarity,timeout):
            print("[OK] Clicked button from '"+src+"' to '"+tgt+"'.")
        else:
            print("[ERROR] Button image for edge "+src+" -> "+tgt+" not found")
            screen.capture().save(cwd, "error_button_"+src+"_"+tgt+".png")
            sys.exit(1)

        # 3) Verify that the target node appears
        print("Verifying node '"+tgt+"': "+tgt_img)
        if search_image(screen,tgt_img,similarity,timeout):
            print("[OK] Node '"+tgt+"' detected")
        else:
            print("[FAIL] Node '"+tgt+"' not found after click.")
            screen.capture().save(cwd, "error_result_"+src+"_"+tgt+".png")
            sys.exit(1)

    print("[COMPLETE] All transitions completed successfully")
    sys.exit(0)

if __name__ == "__main__":
    main()
