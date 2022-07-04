from enum import Enum

class RegionCode(Enum):
    INSIDE = 0b0000
    LEFT = 0b0001
    RIGHT = 0b0010
    BOTTOM = 0b0100
    TOP = 0b1000

class LineClipping(Enum):
    COHEN_SUTHERLAND = 0
    LIAN_BARSK = 1

CLIPPING_REGIONS_2D = [RegionCode.LEFT, RegionCode.RIGHT, RegionCode.TOP, RegionCode.BOTTOM]

class Clipper():
    """
    Clip de ponto no espaço normalizado da window
    Retorna None se o ponto não faz parte 
    da àrea da window
    """
    def point_clipping(point):
        """
        Point deve ser uma lista 
        com uma única tupla com as coordenadas
        do ponto
        """
        (x,y,_) = point

        if(x < 1 and x > -1 and y < 1 and y > -1):
            return point
        else:
            return None

    """
    Clip de linha no espaço normalizado da window
    com o algorítimo Cohen-Sutherland
    Retorna None se não existe segmento de reta
    que faz parte da àrea da window
    """
    def cohen_sutherland_clipping(line):
        """
        Line deve ser uma lista com dois pontos.
        Cada ponto deve ser uma tupla com as coordanadas.
        """
        [initial, final] = line

        clipped = None

        initial_rc = Clipper.region_code(initial)
        final_rc = Clipper.region_code(final)

        while ((initial_rc & final_rc) == 0b0000):
            """
            Se os dois pontos, ou os dois pontos depois de algum recálculo
            que coloca os limites sobre as bordas,
            se encontrarem fora da região central e na mesma região
            clipped == None.
            Se ele se encontrarem ambos na região central
            então foi encontrada o novo segmento de reta.
            """

            if(initial_rc == 0b0000 and final_rc == 0b0000):
                clipped = [initial, final]
                break

            #Calcula a intersecção e reatribui, recalculando a regiao
            if(initial_rc != RegionCode.INSIDE.value):
                initial =  Clipper.cohen_sutherland_intersect(initial, final, initial_rc)
                initial_rc = Clipper.region_code(initial)

            elif(final_rc != RegionCode.INSIDE.value):
                final =  Clipper.cohen_sutherland_intersect(final, initial, final_rc)
                final_rc = Clipper.region_code(final)


        return clipped

    """
    Calcula a intersecção de uma reta com a borda da window, 
    dados dois pontos e uma regiao.
    """
    def cohen_sutherland_intersect(vertex_1, vertex_2, region):
        (x0,y0) = vertex_1
        (x1,y1) = vertex_2

        #Recalcula o ponto para os extremos
        if((region & RegionCode.LEFT.value) != 0b0000):
            m = (y1-y0)/(x1-x0)
            y0 = (m*(-1 - x0)) + y0
            x0 = -1
        elif((region & RegionCode.RIGHT.value) != 0b0000):
            m = (y1-y0)/(x1-x0)
            y0 = ( m*(1 - x0)) + y0
            x0 = 1
        if((region & RegionCode.TOP.value) != 0b0000):
            m = (x1-x0)/(y1-y0)
            x0 = x0 + m*(1 - y0)
            y0 = 1
        elif((region & RegionCode.BOTTOM.value) != 0b0000):
            m = (x1-x0)/(y1-y0)
            x0 = x0 + m*(-1 - y0)
            y0 = -1

        return (x0,y0)

    """
    Calculates region code given a point

    1001|1000|1010
    ____|____|____
    0001|0000|0010
    ____|____|____
        |    |
    0101|0100|0110
    """
    def region_code(point):
        (x,y) = point
        rc = 0
        if(x < -1):
            rc = rc | RegionCode.LEFT.value
        if(x > 1):
            rc = rc | RegionCode.RIGHT.value
        if(y < -1):
            rc = rc | RegionCode.BOTTOM.value
        if(y > 1):
            rc = rc | RegionCode.TOP.value

        return rc


    """
    Clip de linha no espaço normalizado da window
    com o algorítimo de Lian-Barsk
    Retorna None se não existe segmento de reta
    que faz parte da àrea da window
    """
    def lian_barsk_clipping(line):
        """
        Line deve ser uma lista com dois pontos.
        Cada ponto deve ser uma tupla com as coordanadas.
        """
        [initial, final] = line
        (x0,y0) = initial
        (x1,y1) = final

        p1 = -(x1 - x0)
        p2 = -p1
        p3 = -(y1 - y0)
        p4 = -p3
        
        q1 = x0 - (-1)
        q2 = 1 - x0
        q3 = y0 - (-1)
        q4 = 1 - y0
        
        if ((p1 == 0 and q1 < 0) or (p2 == 0 and q2 < 0) or (p3 == 0 and q3 < 0) or (p4 == 0 and q4 < 0)):
            return None

        p = [p1,p2,p3,p4]
        q = [q1,q2,q3,q4]

        pq = [(p1,q1),(p2,q2),(p3,q3),(p4,q4)]

        neg_p_r = [qk/pk for (pk,qk) in pq if pk != 0 and pk < 0]
        pos_p_r = [qk/pk for (pk,qk) in pq if pk != 0 and pk > 0]
        
        neg_p_r.append(0)
        pos_p_r.append(1)
        
        zeta1 = max(neg_p_r)
        zeta2 = min(pos_p_r)

        if(zeta1 > zeta2):
            return None
        
        (new_x0, new_y0) = initial
        (new_x1, new_y1) = final
        
        if(zeta1 > 0):
            new_x0 = x0 + zeta1*(x1-x0)
            new_y0 = y0 + zeta1*(y1-y0)
        
        if(zeta2 < 1):
            new_x1 = x0 + zeta2*(x1-x0)
            new_y1 = y0 + zeta2*(y1-y0)
        
        return [(new_x0,new_y0),(new_x1,new_y1)]


    """
    Clip de objetos Sutherland-Hodgman
    com clip de linhas Cohen-Sutherland
    """
    def sutherland_hodgman_clipping(polygon):

        clipped = polygon.copy()
        curr_clip = None

        for region in CLIPPING_REGIONS_2D:
            curr_clip = clipped.copy()
            length = len(curr_clip)
            clipped = []

            for i in range(length):
                curr = curr_clip[i]
                prev = curr_clip[(i - 1) % length]
                Clipper.sutherland_hodgman_step(curr, prev, length, clipped, i, region)


        if(len(clipped) == 0):
            clipped = None
        return clipped


    def sutherland_hodgman_step(curr, prev,length,  clipped, i, region):

        """
        Clipa a linha com cohen sutherland
        """
        curr_rc = Clipper.region_code(curr)
        prev_rc = Clipper.region_code(prev)
        
        if((curr_rc & region.value) == 0b0000):
            #curr está dentro
            if((prev_rc & region.value) != 0b0000):
                #curr está dentro e prev está fora
                intersect =  Clipper.cohen_sutherland_intersect(curr, prev, region.value)
                clipped.append(intersect)

            #já que está dentro, fica
            clipped.append(curr)
        elif((prev_rc & region.value) == 0b0000):
            #curr está fora e prev está dentro
            intersect =  Clipper.cohen_sutherland_intersect(prev, curr, region.value)
            clipped.append(intersect)

            #curr é "eliminado"
            """
            Apesar de prev estar dentro seu valor não é adicionado agora,
            pois esse vértice foi adicionado quando foi atribuído à curr,
            na iteração anterior
            """

    """
    Clipa as coordenadas consecutivas duas a duas
    e constroi um conjunto de retas clipadas
    Para curvas ou wireframes não fechados
    """
    def line_set_clipping(coords, line_clipping):
        line_set = []
        for i in range(len(coords)-1):
            _curr = coords[i]
            _next = coords[i+1]

            clipped = None
            if(line_clipping == LineClipping.LIAN_BARSK):
                clipped = Clipper.lian_barsk_clipping([_curr, _next])
            else:
                clipped = Clipper.cohen_sutherland_clipping([_curr, _next])

            if(clipped != None):
                line_set += clipped

        if(len(line_set) == 0):
            return None

        return line_set