function ukData = loadUKExpenditureData(filename)
%LOADUKEXPENDITUREDATA Parse the 'Expenditures (U.K.)' sheet.
%   Returns a struct with per-age-block quintile expenditures,
%   weekly income quintiles, average persons, and regional data.

    raw = readcell(filename, 'Sheet', 'Expenditures (U.K.)');

    ukData.ageLabels  = {'<30','30-49','50-64','65-74','>74'};
    ukData.ageBounds  = [0 29; 30 49; 50 64; 65 74; 75 Inf];
    blockStarts       = [4, 21, 38, 55, 72];

    % Weekly income by quintile (right-side table, row 5, cols J-N = 10:14)
    ukData.quintileIncome = parseRow(raw, 5, 10:14);

    nBlocks = numel(blockStarts);
    ukData.avgPersons     = zeros(nBlocks, 5);
    ukData.essentialWeekly = zeros(nBlocks, 5);
    ukData.avgPersonsAll  = zeros(nBlocks, 1);

    for b = 1:nBlocks
        r0 = blockStarts(b);
        % Average number of persons per household: row r0+2, cols B-F (2:6) and G (7)
        ukData.avgPersons(b,:) = parseRow(raw, r0+2, 2:6);
        ukData.avgPersonsAll(b) = parseCell(raw, r0+2, 7);

        % Essential categories (offsets from block header row):
        %   Food & non-alcoholic drinks: r0+4
        %   Housing(net), fuel & power:  r0+7
        %   Transport:                   r0+10
        food      = parseRow(raw, r0+4, 2:6);
        housing   = parseRow(raw, r0+7, 2:6);
        transport = parseRow(raw, r0+10, 2:6);
        ukData.essentialWeekly(b,:) = food + housing + transport;
    end

    % ---- Regional data (right side, rows 8-25, cols I-N = 9:14) ----
    ukData.regionLabels = {'England','Wales','Scotland','Northern Ireland'};
    % Regions in cols J-M (10:13), All UK in col N (14)
    % Expenditure category rows on right side: 12-24
    regionCatRows = 12:24;
    ukData.regionAllExpendWeekly = zeros(1, 4);
    nationalTotal = 0;
    for k = 1:numel(regionCatRows)
        rr = regionCatRows(k);
        ukData.regionAllExpendWeekly = ukData.regionAllExpendWeekly + parseRow(raw, rr, 10:13);
        nationalTotal = nationalTotal + parseCell(raw, rr, 14);
    end
    ukData.nationalAllExpendWeekly = nationalTotal;
end

function vals = parseRow(raw, row, cols)
    vals = zeros(1, numel(cols));
    for i = 1:numel(cols)
        vals(i) = parseCell(raw, row, cols(i));
    end
end

function v = parseCell(raw, row, col)
    c = raw{row, col};
    if ismissing(c)
        v = 0;
    elseif isnumeric(c) && ~isnan(c)
        v = c;
    elseif ischar(c) || isstring(c)
        s = strrep(char(c), ',', '');
        n = str2double(s);
        if isnan(n), v = 0; else, v = n; end
    else
        v = 0;
    end
end
