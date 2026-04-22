%% SCRIPT DE VISUALIZACIÓN DE BARRIDOS
close all; clear; clc;

folder = 'sim_results'; % La carpeta que creamos antes
archivos = dir(fullfile(folder, 'Theta80_G_omega*.mat')); % Buscamos todos los .mat

if isempty(archivos)
    error('No se encontraron archivos en la carpeta %s', folder);
end

figure('Name', 'Respuesta del Pendulo', 'Color', 'w');
hold on; grid on;

vTheta = cell(length(archivos), 1);
vX = cell(length(archivos), 1);
vF = cell(length(archivos), 1);
vTime = cell(length(archivos), 1);

for i = 1:length(archivos)

    pathCompleto = fullfile(folder, archivos(i).name);
    data = load(pathCompleto);
    

    vTheta{i} = 180/pi*data.theta;
    vTime{i} = data.time; 

    % nombreLimpio = strrep(archivos(i).name, '.mat', '');
    % nombreLimpio = strrep(nombreLimpio, 'Sim_Angulo_', 'Init: ');
    % nombreLimpio = erase(archivos(i).name, ["Sim_Angulo_", ".mat"]); % Extrae el número
    legendaTexto = sprintf('G_{x}=%d', i);
    
    plot(vTime{i}, vTheta{i}, 'LineWidth', 1.5, 'DisplayName', legendaTexto);
end

lgd = legend('show');
t = title(lgd, '$\theta_0=80^\circ$');
set(t, 'Interpreter', 'latex');

xlabel('Tiempo $t$ [s]', 'Interpreter', 'latex', 'FontSize', 13);
ylabel('Posicion $x(t)$ [deg]', 'Interpreter', 'latex', 'FontSize', 13);
title('Barrido de la Ganancia $G_\omega$', ...
      'Interpreter', 'latex', 'FontSize', 15);


set(gca, 'TickLabelInterpreter', 'latex', ...
         'FontSize', 11, ...
         'XMinorGrid', 'on', ...
         'YMinorGrid', 'on', ...
         'Box', 'on'); 

% Muchas curvas: usar un mapa de colores (colormap)
colormap(jet(length(archivos)));

%%
figure('Name', 'Movimiento del Carrito', 'Color', 'w');
hold on; grid on;

for i = 1:length(archivos)

    pathCompleto = fullfile(folder, archivos(i).name);
    data = load(pathCompleto);

    vX{i} = data.x;
    vTime{i} = data.time; 

    % nombreLimpio = strrep(archivos(i).name, '.mat', '');
    % nombreLimpio = strrep(nombreLimpio, 'Sim_Angulo_', 'Init: ');
    % nombreLimpio = erase(archivos(i).name, ["Sim_Angulo_", ".mat"]); % Extrae el número
    legendaTexto = sprintf('G_{x}=%d', i);
    
    plot(vTime{i}, vX{i}, 'LineWidth', 1.5, 'DisplayName', legendaTexto);
end

lgd = legend('show');
t = title(lgd, '$\theta_0=80^\circ$');
set(t, 'Interpreter', 'latex');

xlabel('Tiempo $t$ [s]', 'Interpreter', 'latex', 'FontSize', 13);
ylabel('Posicion $x(t)$ [m]', 'Interpreter', 'latex', 'FontSize', 13);

title('Barrido de la Ganancia $G_\omega$', ...
      'Interpreter', 'latex', 'FontSize', 15);


set(gca, 'TickLabelInterpreter', 'latex', ...
         'FontSize', 11, ...
         'XMinorGrid', 'on', ...
         'YMinorGrid', 'on', ...
         'Box', 'on'); 

% Muchas curvas: usar un mapa de colores (colormap)
colormap(jet(length(archivos)));

%%
figure('Name', 'Grafico de Fuerzas', 'Color', 'w');
hold on; grid on;

vForce= cell(length(archivos), 1); 

for i = 1:length(archivos)

    pathCompleto = fullfile(folder, archivos(i).name);
    data = load(pathCompleto);
    

    vF{i} = data.F;
    vTime{i} = data.time;
    

    % nombreLimpio = strrep(archivos(i).name, '.mat', '');
    % nombreLimpio = strrep(nombreLimpio, 'Sim_Angulo_', 'Init: ');
    % nombreLimpio = erase(archivos(i).name, ["Sim_Angulo_", ".mat"]); % Extrae el número
    legendaTexto = sprintf('G_{x}=%d', i);
    
    plot(vTime{i}, vF{i}, 'LineWidth', 1.5, 'DisplayName', legendaTexto);
end

lgd = legend('show');
t = title(lgd, '$\theta_0=80^\circ$');
set(t, 'Interpreter', 'latex');


xlabel('Tiempo $t$ [s]', 'Interpreter', 'latex', 'FontSize', 13);
ylabel('Fuerza de Control $F_{FLC}(t)$ [N]', 'Interpreter', 'latex', 'FontSize', 13);
title('Barrido de la Ganancia $G_\omega$', ...
      'Interpreter', 'latex', 'FontSize', 15);

set(gca, 'TickLabelInterpreter', 'latex', ...
         'FontSize', 11, ...
         'XMinorGrid', 'on', ...
         'YMinorGrid', 'on', ...
         'Box', 'on'); 

% Muchas curvas: usar un mapa de colores (colormap)
colormap(jet(length(archivos)));

% Guarda el gráfico en alta resolución (300 DPI) para el PDF de la tesis
% exportgraphics(gcf, 'Variacion Theta y VI Nulos2.png', 'Resolution', 300);
