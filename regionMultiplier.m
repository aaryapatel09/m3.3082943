function f = regionMultiplier(region, country, usData, ukData)
%REGIONMULTIPLIER Return regional cost-of-living multiplier relative to national average.
%   f = regionMultiplier(region, country, usData, ukData)

    if strcmpi(country, 'US')
        rIdx = find(strcmpi(usData.regionLabels, region), 1);
        if isempty(rIdx)
            f = 1.0;
            return;
        end
        regionRatio   = usData.regionAllExpend(rIdx) / usData.regionIncome(rIdx);
        nationalRatio = usData.nationalAllExpend / usData.nationalIncome;
        f = regionRatio / nationalRatio;
    else
        rIdx = find(strcmpi(ukData.regionLabels, region), 1);
        if isempty(rIdx)
            f = 1.0;
            return;
        end
        f = ukData.regionAllExpendWeekly(rIdx) / ukData.nationalAllExpendWeekly;
    end
end
