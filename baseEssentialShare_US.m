function theta = baseEssentialShare_US(age, usData)
%BASEESSENTIALSHARE_US Return essential-spend / income ratio for a US age group.
%   theta = baseEssentialShare_US(age, usData)

    idx = mapAgeToIndex(age, usData.ageBounds);
    theta = usData.essentialExpend(idx) / usData.meanIncome(idx);
end

function idx = mapAgeToIndex(age, bounds)
    idx = size(bounds, 1);  % default: last group
    for k = 1:size(bounds, 1)
        if age >= bounds(k,1) && age <= bounds(k,2)
            idx = k;
            return;
        end
    end
end
