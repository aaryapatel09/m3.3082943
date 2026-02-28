function usData = loadUSExpenditureData(filename)
%LOADUSEXPENDITUREDATA Parse the 'Expenditures (U.S.)' sheet.
%   Returns a struct with age-group incomes, essential expenditures,
%   and regional expenditure data.

    raw = readcell(filename, 'Sheet', 'Expenditures (U.S.)');

    usData.ageLabels = raw(3, 2:8);
    usData.ageBounds = [0 24; 25 34; 35 44; 45 54; 55 64; 65 74; 75 Inf];

    usData.meanIncome     = parseRow(raw, 4, 2:8);
    usData.allExpend      = parseRow(raw, 11, 2:8);

    essRows = [12 13 14 19 20 25];
    usData.essentialExpend = zeros(1, 7);
    for k = 1:numel(essRows)
        usData.essentialExpend = usData.essentialExpend + parseRow(raw, essRows(k), 2:8);
    end

    usData.regionLabels       = {'Northeast','Midwest','South','West'};
    usData.regionIncome       = parseRow(raw, 4, 9:12);
    usData.regionAllExpend    = parseRow(raw, 11, 9:12);

    usData.regionEssentialExpend = zeros(1, 4);
    for k = 1:numel(essRows)
        usData.regionEssentialExpend = usData.regionEssentialExpend + parseRow(raw, essRows(k), 9:12);
    end

    usData.nationalIncome    = mean(usData.regionIncome);
    usData.nationalAllExpend = mean(usData.regionAllExpend);
end

function vals = parseRow(raw, row, cols)
    vals = zeros(1, numel(cols));
    for i = 1:numel(cols)
        v = raw{row, cols(i)};
        if ismissing(v)
            vals(i) = 0;
        elseif isnumeric(v)
            vals(i) = v;
        elseif ischar(v) || isstring(v)
            n = str2double(strrep(char(v), ',', ''));
            if isnan(n), vals(i) = 0; else, vals(i) = n; end
        else
            vals(i) = 0;
        end
    end
end
