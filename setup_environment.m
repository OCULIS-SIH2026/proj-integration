% SETUP_ENVIRONMENT
% Initializes the MATLAB environment for the Unified RetinaAI Screening Engine.
% Adds all matlab_pipeline modules and Simulink simulation scripts to the MATLAB search path.

function setup_environment()
    rootPath = fileparts(mfilename('fullpath'));
    matlabPipelinePath = fullfile(rootPath, 'matlab_pipeline');
    
    subDirs = {
        'main', ...
        'input', ...
        'quality', ...
        'enhancement', ...
        'anatomy', ...
        'lesions', ...
        'model', ...
        'explainability', ...
        'decision', ...
        'report', ...
        'simulink', ...
        'tests', ...
        'utils'
    };

    fprintf('====================================================\n');
    fprintf('  Initializing Unified RetinaAI Pipeline...\n');
    fprintf('====================================================\n');

    % Add matlab_pipeline subdirectories
    for i = 1:numel(subDirs)
        dirPath = fullfile(matlabPipelinePath, subDirs{i});
        if exist(dirPath, 'dir')
            addpath(dirPath);
            fprintf('  [+] Added to path: matlab_pipeline/%s\n', subDirs{i});
        end
    end

    % Add root simulink folder
    simulinkPath = fullfile(rootPath, 'simulink');
    if exist(simulinkPath, 'dir')
        addpath(simulinkPath);
        fprintf('  [+] Added to path: simulink/\n');
    end

    addpath(matlabPipelinePath);
    addpath(rootPath);
    fprintf('\nRetinaAI MATLAB & Simulink Environment successfully initialized.\n');
    fprintf('You can now run:\n');
    fprintf('  - runAllPipelineTests        (Execute 10-phase test harness)\n');
    fprintf('  - screenFundusImage("path")  (Single-command patient screening)\n');
    fprintf('  - simulateScreeningWorkflow  (100k+ telemedicine queue simulation)\n');
    fprintf('====================================================\n');
end
