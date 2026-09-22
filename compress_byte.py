import heapq, json, sys

class Node:
    def __init__(self, value, freq, c_l, c_r):
        self.value = value
        self.freq = freq
        self.c_l = c_l
        self.c_r = c_r

    def __lt__(self, other):
        return self.freq < other.freq

def count_occ(text):
    dic = {}
    for c in text:
        if c not in dic:
            dic[c] = 1
        else:
            dic[c] += 1
    return dic


def dic_to_heap(dic):
    heap = []
    for k in dic:
        node = Node(k, dic[k], None, None)
        heap.append(node)
    heapq.heapify(heap)
    return heap

def dfs_binary(node, pre, dic):
    if node.value is not None:
        dic[node.value] = pre or "0"  # "0" si l'arbre n'a qu'une feuille
    else:
        l_pre = pre + "0"
        r_pre = pre + "1"
        dfs_binary(node.c_l, l_pre, dic)
        dfs_binary(node.c_r, r_pre, dic)

def huffman(file):
    with open(file, 'rb') as f:
        data = f.read()
        heap_occ = dic_to_heap(count_occ(data))
        while len(heap_occ) > 1:
            left = heapq.heappop(heap_occ)
            right = heapq.heappop(heap_occ)
            parent = Node(None, left.freq+right.freq, left, right)
            heapq.heappush(heap_occ, parent)
        huffman_code = {}
        if heap_occ:  # fichier vide : pas d'arbre
            dfs_binary(heap_occ[0], "", huffman_code)
        current_octet = 0
        byte = bytearray()
        cpt_bytes = 0
        for c in data:
            code = huffman_code[c]
            for bit in code:
                current_octet <<= 1
                if bit == '1':
                    current_octet |= 1
                cpt_bytes +=1

                if cpt_bytes == 8:
                    byte.append(current_octet)
                    current_octet = 0
                    cpt_bytes = 0
        padding_length =0
        if cpt_bytes > 0 :
            padding_length = 8 - cpt_bytes
            current_octet <<= padding_length
            byte.append(current_octet)
        huffman_code["_PADDING_"] = padding_length
        json_dic = json.dumps(huffman_code)

        with open(file + ".huff", 'wb') as o:
            o.write(json_dic.encode("utf-8"))
            o.write(b'\n')
            o.write(byte)


def decompress(huff_file) :
    with open(huff_file, 'rb') as inp:
        header_str = inp.readline().decode('utf-8')
        header_dic = json.loads(header_str)
        padding = header_dic.pop("_PADDING_")
        inversed_dico = {valeur: int(cle) for cle, valeur in header_dic.items()}
        texte = ""
        data = inp.read()
        for octet in data:
            octet_trad = f"{octet:08b}"
            texte += octet_trad
        if padding > 0:
            texte = texte[:-padding] #enleve les zéros artificiels
        byte = bytearray()
        tamp = ""
        for bit in texte:
            tamp += bit
            if tamp in inversed_dico:
                byte.append(inversed_dico[tamp])
                tamp = ""

        output_name = huff_file.replace(".huff", "_restaure")
        with open(output_name, 'wb') as out:
            out.write(byte)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Utilisation : python3 compress.py <c ou d> <nom_du_fichier>")
    else:
        fichier = sys.argv[2]
        action = sys.argv[1]

        if action == "c":
            if not fichier.endswith(".huff"):
                huffman(fichier)
                print("Compression terminée.")
            else:
                print("Le fichier est déjà compressé (.huff).")

        elif action == "d":
            if fichier.endswith(".huff"):
                decompress(fichier)
                print("Décompression terminée.")
            else:
                print("Fichier non compressé ou extension invalide (attendue: .huff).")

        else:
            print("Mauvais paramètre : entrez c pour compresser ou d pour décompresser.")
