[intrinsicMatrix, distortionCoefficients] = cameraIntrinsicsToOpenCV(cameraParams);
writematrix(intrinsicMatrix,'mtx.csv')
writematrix(distortionCoefficients,'dist.csv')