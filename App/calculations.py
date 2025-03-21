from typing import Callable
import numpy as np
import random as rd


def calculate_darboux_sums(points:list[float], func: Callable):
    lower_sum: float = 0
    upper_sum: float = 0
    max_s: float = 0
    aux_max: float = 0
    lower_area:float = 0
    upper_area:float = 0
    details: dict[str, float] = {}

    # Para cada subintervalo en la partición
    for i in range(len(points) - 1):
        # Límites del subintervalo
        a: float = points[i]       
        b: float = points[i+1]     
        delta_x:float = b - a
        
        # Indice del puntos inicial del mayor subintervalo
        if delta_x > aux_max:
            aux_max = delta_x
            max_s = i
        
        # Puntos para la aproximacion 
        x_values = np.linspace(a, b, 100)
        y_values = func(x_values)

        # Máximo y mínimo de la función en el subintervalo
        min_val:float = np.min(y_values)
        max_val:float = np.max(y_values)
        
        # Calcular área para este subintervalo
        lower_area = min_val * delta_x
        upper_area = max_val * delta_x

        # Acumular sumas
        lower_sum += lower_area
        upper_sum += upper_area

    # Guardar detalles de este subintervalo para visualización posterior
    details = {
        'lower_sum': lower_sum,
        'upper_sum': upper_sum,
        'max_subinterval': max_s
    }
    return points, details
def calculate_add_point(points: list[float], func: Callable, details: dict[str, float]):
    ms_index:int = int(details['max_subinterval'])
    ms_size:float = points[ms_index + 1] - points[ms_index]

    # Calcular el area del intervalo que se va a dividir 
    x_values = np.linspace(points[ms_index], points[ms_index + 1], 100)
    y_values = func(x_values)

    min_val:float = np.min(y_values)
    max_val:float = np.max(y_values)

    lower_area = min_val * ms_size
    upper_area = max_val * ms_size


    lower_sum: float = details['lower_sum'] - lower_area
    upper_sum: float = details['upper_sum'] - upper_area
    max_s: float = 0
    aux_max: float = 0
    details: dict[str, float] = {}

    new_point = rd.random() * ms_size + points[ms_index]
    points.insert(ms_index + 1, new_point)
    
    for i in range(len(points) - 1):
        a: float = points[i]
        b: float = points[i+1]
        delta_x:float = b - a

        # Indice del punto inicial del mayor subintervalo
        if delta_x > aux_max:
            aux_max = delta_x
            max_s = i
         
        if i!=ms_index and i!=ms_index+1:
            continue
         
    
        x_values = np.linspace(a, b, 100)
        y_values = func(x_values)
    
        min_val:float = np.min(y_values)
        max_val:float = np.max(y_values)
    
        lower_area = min_val * delta_x
        upper_area = max_val * delta_x
    
        lower_sum += lower_area
        upper_sum += upper_area
        
    details = {
        'lower_sum': lower_sum,
        'upper_sum': upper_sum,
        'max_subinterval': max_s
    }
    return points, details