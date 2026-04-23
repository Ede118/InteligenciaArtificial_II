%% Script de Barrido Paramétrico - Proyecto Péndulo/Carrito

model = 'Pendulo_Invertido';
load_system(model);

% Definición del vector de prueba (ejemplo: barrido de ángulos iniciales)

Delta = 1;
v = linspace(Delta, Delta+29, 30);
numSims = length(v);

% Preparamos un array de objetos de simulación
for i = 1:numSims
    simIn(i) = Simulink.SimulationInput(model);
    
    simIn(i) = simIn(i).setVariable('theta_0', 80*pi/180);
    simIn(i) = simIn(i).setVariable('dtheta_0', 0);
    
    simIn(i) = simIn(i).setVariable('x_0', 0);
    simIn(i) = simIn(i).setVariable('dx_0', 0);

    simIn(i) = simIn(i).setVariable('G_omega', v(i));

    % simIn(i) = simIn(i).setModelParameter('InitMsgLevel', 'none');
    % simIn(i) = simIn(i).setPreSimFcn(@(x) warning('off', 'all'));
end

% Ejecución masiva
% Si tenés Parallel Computing Toolbox, usá 'parsim', si no 'sim'
out = sim(simIn);

if ~exist('Curvas/sim_results', 'dir')
    mkdir('Curvas/sim_results');
end

for i = 1:numSims
    % Extraemos los datos de cada simulación
    % Accedemos por el nombre que le pusiste a la señal en Simulink
    data.time  = out(i).logsout.getElement('x').Values.Time;
    data.x     = out(i).logsout.getElement('x').Values.Data;
    data.v     = out(i).logsout.getElement('dx').Values.Data;
    data.theta = out(i).logsout.getElement('theta').Values.Data;
    data.omega = out(i).logsout.getElement('dtheta').Values.Data;
    data.F     = out(i).logsout.getElement('F').Values.Data;
    
    % Guardamos en un .mat único por corrida
    filename = sprintf('Curvas/sim_results/Theta80_G_omega%02d.mat', i);
    save(filename, '-struct', 'data');
end

fprintf('Simulaciones completadas y guardadas en /Curvas/sim_results\n');