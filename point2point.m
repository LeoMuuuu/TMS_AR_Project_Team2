
function [R,p] = point2point(A,B)

    n = size(A,1);        % Length of Point Sets
    
    % Calculate centroids of S and M point sets
    a_centroid = (1/n) * sum(A);
    b_centroid = (1/n) * sum(B);
    a_centroid = a_centroid';
    b_centroid = b_centroid';
    
    % Point Deviations from centroid  
    A_tilda = A - a_centroid';
    B_tilda = B - b_centroid';
 
    
    %-------------------- Find R that minimizes SSE --------------------% 
    
    % H Matrix for Singular Value Decomposition
    H = zeros(3,3);
    x = 1; y = 2; z = 3;
        
    % Build H 
    for i = 1:n
        H = H + [A_tilda(i,x)*B_tilda(i,x), A_tilda(i,x)*B_tilda(i,y), A_tilda(i,x)*B_tilda(i,z);
                 A_tilda(i,y)*B_tilda(i,x), A_tilda(i,y)*B_tilda(i,y), A_tilda(i,y)*B_tilda(i,z);
                 A_tilda(i,z)*B_tilda(i,x), A_tilda(i,z)*B_tilda(i,y), A_tilda(i,z)*B_tilda(i,z)];
    end
    
    % SVD Decomposition 
    [U,S,V] = svd(H);
        
    % Calculate Rotation Matrix, R 
    R = V*transpose(U);
        
    % Use Section IV of K. Arun et. al to change mirror and make valid matrix 
    % If this does not work, this algorithm cannot be used
    if (det(R) < 0)
        V(:,3) = -V(:,3);
        R = V * U';
        
        if (det(R) < 0)
        end
    end
        
    %-------------------- Find translation vector --------------------% 
        
    % Compute p, Translation
    p = b_centroid - R*a_centroid;
            
end