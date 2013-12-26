addpath ~/research/tools/file_converters/
addpath ~/research/tools/file_converters/xml_io_tools/

s1= ReadSurface('/Volumes/Users/sjoshi/Desktop/srgiorgio1263_s0003_11_C2S1.left.mid.cortex.svreg.dfs');

% Simulate

N1 = 40;
N2 = 50;
s2 = s1;
for i = 1:N1
    T1 = round(length(s1.attributes)*5/100);
    T2 = round(length(s1.attributes)*50/100);
    T3 = length(s1.attributes) - T1 - T2;
    
    thickness1 = ([2.3 + 0.4.*randn(1,T1), 3.1 + 0.01*randn(1,T2), 1.2 + 0.01*randn(1,T3) ]); %2.5 +- 2mm
    s1.attributes = thickness1;
    WriteSurface(sprintf('~/Desktop/stats/surface_group1_%s.dfs',num2str(i)),s1);
    
    T1 = round(length(s1.attributes)*5/100);
    T2 = round(length(s1.attributes)*50/100);
    T3 = length(s1.attributes) - T1 - T2;
    
    thickness2 = ([5.9 + 0.4.*randn(1,T1), 3.1 + 0.01*randn(1,T2), 1.2 + 0.01*randn(1,T3) ]); %4.5 +- 2mm
    s2.attributes = thickness2;
    WriteSurface(sprintf('~/Desktop/stats/surface_group2_%s.dfs',num2str(i)),s2);
end


% Simulate Age

age1 = 60 + 5*randn(1,40);
age2 = 40 + 5*randn(1,40);