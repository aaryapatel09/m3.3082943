function f = householdMultiplier(h, age, country, usData, ukData)
%HOUSEHOLDMULTIPLIER Economies-of-scale adjustment for household size.
%   f = householdMultiplier(h, age, country, usData, ukData)
%   f = (h / h_bar)^gamma, gamma = 0.7

    gamma = 0.7;

    if strcmpi(country, 'UK')
        bIdx = mapAgeToBlock(age, ukData.ageBounds);
        h_bar = ukData.avgPersonsAll(bIdx);
    else
        % US: approximate average household size by age group
        usHHbyAge = [2.0, 3.0, 3.3, 3.0, 2.5, 2.0, 1.7];
        idx = mapAgeToBlock(age, usData.ageBounds);
        h_bar = usHHbyAge(idx);
    end

    if h_bar <= 0, h_bar = 2.5; end
    f = (h / h_bar) ^ gamma;
end

function idx = mapAgeToBlock(age, bounds)
    idx = size(bounds, 1);
    for k = 1:size(bounds, 1)
        if age >= bounds(k,1) && age <= bounds(k,2)
            idx = k;
            return;
        end
    end
end
