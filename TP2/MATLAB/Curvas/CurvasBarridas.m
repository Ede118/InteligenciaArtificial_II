%% Script de Barrido Paramétrico - Proyecto Péndulo/Carrito
model = '../Pendulo_Invertido';
load_system(model);

% Definición del vector de prueba (ejemplo: barrido de ángulos iniciales)
% theta_init_values = linspace(pi/36, pi/2, 18);

% F = alpha*g*tand(80)
% alpha = 2.1 g = 9.80665
F = 0.5*2.1*9.80665*tand(90);
vG_F = linspace(F, 20*F, 20);
numSims = length(vG_F);



% Preparamos un array de objetos de simulación
for i = 1:numSims
    simIn(i) = Simulink.SimulationInput(model);
    
    simIn(i) = simIn(i).setVariable('theta_0', 90*pi/180);
    simIn(i) = simIn(i).setVariable('dtheta_0', 0);
    
    simIn(i) = simIn(i).setVariable('x_0', 0);
    simIn(i) = simIn(i).setVariable('dx_0', 0);

    simIn(i) = simIn(i).setVariable('G_F', vG_F(i));
end

% Ejecución masiva
% Si tenés Parallel Computing Toolbox, usá 'parsim', si no 'sim'
out = sim(simIn);

%% 3. Guardado en archivos independientes
if ~exist('sim_results', 'dir')
    mkdir('sim_results');
else
    print('Existe el directorio.')
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
    filename = sprintf('Curvas/sim_results/Theta90_G_F%02d.mat', i);
    save(filename, '-struct', 'data');
end

fprintf('Simulaciones completadas y guardadas en /sim_results\n');