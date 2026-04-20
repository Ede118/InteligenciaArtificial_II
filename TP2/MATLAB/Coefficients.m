% Physical Coefficients

m_c =  10;             % kg
m_p =  1;              % kg
l =  0.1;              % m
g = 9.80665;           % m/s2

% Reemplazos introducidos
alpha = m_p + m_c;
lambda = 4/3 * m_p * l^2;
mu = m_p * l;

% Definicion de Amortiguamientos
zeta_c = 0.05;              % adim
zeta_p = 0.10;              % adim

% Frecuencia Natural del pendulo
omega_p = sqrt(mu*g/(lambda-mu^2/alpha));
f_p = omega_p/(2*pi);

% Coeficientes de friccion
beta = 2*zeta_p*omega_p*(lambda-mu^2/alpha);
b = 2*zeta_c*omega_p*alpha;

% Fuerza de equilibrio para caso mas desventajoso
F_equilibrium = alpha*g*tand(75);
