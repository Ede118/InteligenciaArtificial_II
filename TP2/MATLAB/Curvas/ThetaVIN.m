%% SCRIPT DE VISUALIZACIÓN DE BARRIDOS
clear; clc;

folder = '../sim_results'; % La carpeta que creamos antes
archivos = dir(fullfile(folder, '*.mat')); % Buscamos todos los .mat

if isempty(archivos)
    error('No se encontraron archivos en la carpeta %s', folder);
end

figure('Name', 'Comparativa de Barrido de Angulos', 'Color', 'w');
hold on; grid on;

theta_init_values = linspace(pi/36, pi/2, 18);
theta_init_values = theta_init_values * 180/pi;

vTheta = cell(length(archivos), 1); 
vTime = cell(length(archivos), 1);

for i = 1:length(archivos)

    pathCompleto = fullfile(folder, archivos(i).name);
    data = load(pathCompleto);
    

    vTheta{i} = 180/pi*data.theta;
    vTime{i} = data.time;
    

    % nombreLimpio = strrep(archivos(i).name, '.mat', '');
    % nombreLimpio = strrep(nombreLimpio, 'Sim_Angulo_', 'Init: ');
    nombreLimpio = erase(archivos(i).name, ["Sim_Angulo_", ".mat"]); % Extrae el número
    legendaTexto = sprintf('\\theta_0 = %.1f^\\circ', theta_init_values(i));
    
    plot(vTime{i}, vTheta{i}, 'LineWidth', 1.5, 'DisplayName', legendaTexto);
end

lgd = legend('show');
set(lgd, 'Location', 'northeastoutside', ...
         'FontSize', 11);
title(lgd, 'Condiciones Iniciales');


xlabel('Tiempo $t$ [s]', 'Interpreter', 'latex', 'FontSize', 13);
ylabel('Angulo $\theta(t)$ [deg]', 'Interpreter', 'latex', 'FontSize', 13);
title('Respuesta Temporal del Pendulo - Barrido de $\theta_0$', ...
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
