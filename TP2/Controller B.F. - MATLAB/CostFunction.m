function cost = CostFunction(fis)
    % 1. Asignar el FIS que está probando el Algoritmo Genético al Workspace
    assignin('base', 'fis_actual', fis);
    
    % 2. Correr la simulación de Simulink (nombre de tu archivo .slx)
    % 'CaptureErrors' evita que el GA se detenga si la planta explota
    simOut = sim('Model.slx', 'CaptureErrors', 'on');
    
    % 3. Extraer el error (suponiendo que usaste un bloque 'To Workspace' llamado 'error_theta')
    t = simOut.error_theta.Time;
    e = simOut.error_theta.Data;
    
    % 4. Calcular el Índice de Desempeño (ejemplo: IAE - Integral del Error Absoluto)
    % El GA intentará MINIMIZAR este valor.
    cost = trapz(t, abs(e)); 
    
    % Penalización: Si el péndulo se cae (error > 90°), dar un costo altísimo
    if max(abs(e)) > pi/2
        cost = cost + 1000;
    end
end