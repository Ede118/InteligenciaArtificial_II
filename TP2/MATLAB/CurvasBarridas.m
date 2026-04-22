%% Script de Barrido Paramétrico - Proyecto Péndulo/Carrito
model = 'Pendulo_Invertido';
load_system(model);

% Definición del vector de prueba (ejemplo: barrido de ángulos iniciales)
theta_init_values = linspace(-pi/4, pi/4, 10); % 10 puntos entre -45 y 45 grados
numSims = length(theta_init_values);
    
% Preparamos un array de objetos de simulación
for i = 1:numSims
    simIn(i) = Simulink.SimulationInput(model);
    
    % Suponiendo que en tu bloque 'Integrator' de theta tenés la variable 'theta_0'
    % o que definiste 'theta_0' en el Mask de tu subsistema.
    simIn(i) = simIn(i).setVariable('theta_0', theta_init_values(i));
    simIn(i) = simIn(i).setVariable('x_0', 0); % Posición inicial nula
end

% Ejecución masiva
% Si tenés Parallel Computing Toolbox, usá 'parsim', si no 'sim'
out = sim(simIn); 

%% 3. Guardado en archivos independientes
if ~exist('sim_results', 'dir')
    mkdir('sim_results');
end

for i = 1:numSims
    % Extraemos los datos de cada simulación
    % Accedemos por el nombre que le pusiste a la señal en Simulink
    data.time  = out(i).logsout.getElement('x').Values.Time;
    data.x     = out(i).logsout.getElement('x').Values.Data;
    data.v     = out(i).logsout.getElement('v').Values.Data;
    data.theta = out(i).logsout.getElement('theta').Values.Data;
    data.omega = out(i).logsout.getElement('omega').Values.Data;
    data.F     = out(i).logsout.getElement('F').Values.Data;
    
    % Guardamos en un .mat único por corrida
    filename = sprintf('sim_results/sweep_theta_%02d.mat', i);
    save(filename, '-struct', 'data');
end

fprintf('Simulaciones completadas y guardadas en /sim_results\n');