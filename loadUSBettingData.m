function usBetData = loadUSBettingData(filename)
%LOADUSBETTINGDATA Parse the 'Online Sports Betting Personal' sheet.
%   Returns a struct with account prevalence, win/lose stats,
%   chase/large-bet percentages, and monthly wager distributions.

    raw = readcell(filename, 'Sheet', 'Online Sports Betting Personal ');

    % Column mapping (left side):
    %   B=2 Total2025, C=3 Total2024, D=4 Male, E=5 Female,
    %   F=6 Age18-34, G=7 Age35-49, H=8 Age50-64, I=9 Age65+,
    %   J=10 NoCollege, K=11 BA+

    usBetData.hasAccount  = parseDemoRow(raw, 4);
    usBetData.chasePercent = parseDemoRow(raw, 40);
    usBetData.bet100plus  = parseDemoRow(raw, 41);
    usBetData.bet500plus  = parseDemoRow(raw, 42);

    usBetData.winMore     = parseDemoRow(raw, 19);
    usBetData.loseMore    = parseDemoRow(raw, 20);
    usBetData.breakEven   = parseDemoRow(raw, 21);

    % Monthly wager distribution (right side, rows 15-19, cols N-P = 14:16)
    % Average across sports to get representative $1-100, $101-500, $500+
    wagerMatrix = zeros(5, 3);
    for k = 1:5
        wagerMatrix(k,:) = parseRowNum(raw, 14+k, 14:16);
    end
    usBetData.monthlyWagerPct = mean(wagerMatrix, 1);

    % Betting frequency (right side, rows 3-10, col N=14 is US)
    usBetData.bettingFreqLabels = cell(1, 8);
    usBetData.bettingFreqUS     = zeros(1, 8);
    for k = 1:8
        usBetData.bettingFreqLabels{k} = safeStr(raw{2+k, 13});
        usBetData.bettingFreqUS(k)     = safeNum(raw{2+k, 14});
    end
end

function s = parseDemoRow(raw, row)
    s.total    = safeNum(raw{row, 2});
    s.male     = safeNum(raw{row, 4});
    s.female   = safeNum(raw{row, 5});
    s.age18_34 = safeNum(raw{row, 6});
    s.age35_49 = safeNum(raw{row, 7});
    s.age50_64 = safeNum(raw{row, 8});
    s.age65p   = safeNum(raw{row, 9});
    s.noCollege = safeNum(raw{row, 10});
    s.baPlus   = safeNum(raw{row, 11});
end

function vals = parseRowNum(raw, row, cols)
    vals = zeros(1, numel(cols));
    for i = 1:numel(cols)
        vals(i) = safeNum(raw{row, cols(i)});
    end
end

function v = safeNum(c)
    if ismissing(c)
        v = 0;
    elseif isnumeric(c) && ~isnan(c)
        v = c;
    elseif ischar(c) || isstring(c)
        v = str2double(strrep(char(c), ',', ''));
        if isnan(v), v = 0; end
    else
        v = 0;
    end
end

function s = safeStr(c)
    if ismissing(c)
        s = '';
    elseif ischar(c) || isstring(c)
        s = char(c);
    elseif isnumeric(c)
        s = num2str(c);
    else
        s = '';
    end
end
