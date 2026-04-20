classdef PendulumAnim < matlab.System
    properties (Nontunable)
        L = 0.2; 
        W = 0.6; 
        H = 0.25;
        XLim = [-15, 15];
    end

    properties (Access = private)
        fig; ax; cart; pole; floor;
        w1; w2; % Ruedas
        txt;    % Texto de estado
    end

    methods (Access = protected)
        function setupImpl(obj)
            % Configuración de la figura con estilo limpio
            obj.fig = figure('Name', 'Control de Péndulo Invertido', ...
                             'NumberTitle', 'off', 'Color', 'w');
            obj.ax = axes('Parent', obj.fig, 'FontName', 'Segoe UI', 'FontSize', 10);
            hold(obj.ax, 'on');
            grid(obj.ax, 'off');
            set(obj.ax, 'Box', 'off', 'TickDir', 'out'); % Estilo moderno
            
            axis(obj.ax, 'equal');
            xlim(obj.ax, obj.XLim); 
            ylim(obj.ax, [-0.5, obj.L + 0.8]);

            % 1. El Suelo (Referencia fija)
            obj.floor = line(obj.ax, obj.XLim, [0 0], 'Color', [0.5 0.5 0.5], 'LineWidth', 2);

            % 2. Ruedas (Círculos que se mueven con el carro)
            r_wheel = obj.H/3;
            obj.w1 = progression_circle(obj.ax, 0, r_wheel, r_wheel); 
            obj.w2 = progression_circle(obj.ax, 0, r_wheel, r_wheel);

            % 3. El Carrito (Ahora un poco más estilizado)
            obj.cart = rectangle('Parent', obj.ax, 'Position', [-obj.W/2, r_wheel, obj.W, obj.H], ...
                                 'FaceColor', [0.15 0.15 0.15], 'EdgeColor', 'none', 'Curvature', 0.1);
            
            % 4. El Péndulo (Color vibrante para contraste)
            obj.pole = line('Parent', obj.ax, 'XData', [0 0], 'YData', [obj.H + r_wheel, obj.L], ...
                            'LineWidth', 5, 'Color', [0.85 0.33 0.1], 'Marker', 'o', ...
                            'MarkerFaceColor', 'w', 'MarkerSize', 8);

            % 5. Texto de Telemetría
            obj.txt = text(obj.ax, obj.XLim(1)+0.2, obj.L+0.5, '', ...
                           'VerticalAlignment', 'top', 'FontWeight', 'bold', 'BackgroundColor', 'w');
        end

        function stepImpl(obj, x, theta)
            if ishandle(obj.fig)
                r_wheel = obj.H/3;
                y_base = obj.H + r_wheel;
                
                % Actualizar Carrito y Ruedas
                set(obj.cart, 'Position', [x - obj.W/2, r_wheel, obj.W, obj.H]);
                set(obj.w1, 'Position', [x - obj.W/4 - r_wheel, 0, 2*r_wheel, 2*r_wheel]);
                set(obj.w2, 'Position', [x + obj.W/4 - r_wheel, 0, 2*r_wheel, 2*r_wheel]);
                
                % Actualizar Péndulo
                x_tip = x - obj.L * sin(theta);
                y_tip = y_base + obj.L * cos(theta);
                set(obj.pole, 'XData', [x, x_tip], 'YData', [y_base, y_tip]);
                
                % Actualizar Telemetría (LaTeX para que se vea pro)
                str = sprintf('Position: %.2f m\nAngle: %.2f°', x, rad2deg(theta));
                set(obj.txt, 'String', str);
                
                drawnow limitrate; 
            end
        end
    end

    methods (Static, Access = protected)
        function simMode = getSimulateUsingImpl, simMode = 'Interpreted execution'; end
    end
end

% Función auxiliar para crear las ruedas (fuera de la clase o como método estático)
function h = progression_circle(ax, x, y, r)
    h = rectangle('Parent', ax, 'Position', [x-r, y-r, 2*r, 2*r], ...
                  'Curvature', [1 1], 'FaceColor', [0.4 0.4 0.4], 'EdgeColor', 'k');
end