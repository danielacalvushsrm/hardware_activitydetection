// Ceres Solver - A fast non-linear least squares minimizer
// Copyright 2023 Google Inc. All rights reserved.
// http://ceres-solver.org/
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are met:
//
// * Redistributions of source code must retain the above copyright notice,
//   this list of conditions and the following disclaimer.
// * Redistributions in binary form must reproduce the above copyright notice,
//   this list of conditions and the following disclaimer in the documentation
//   and/or other materials provided with the distribution.
// * Neither the name of Google Inc. nor the names of its contributors may be
//   used to endorse or promote products derived from this software without
//   specific prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
// ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
// LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
// CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
// SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
// INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
// CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
// ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
// POSSIBILITY OF SUCH DAMAGE.
//
// Author of base Code: keir@google.com (Keir Mierle)
//
// A minimal, self-contained bundle adjuster using Ceres, that reads
// files from University of Washington' Bundle Adjustment in the Large dataset:
// http://grail.cs.washington.edu/projects/bal
//
// Adapted for 3D Problem by Daniela Calvus daniela.calvus@hs-rm.de Hochschule Rhein Main

#include <cmath>
#include <cstdio>
#include <string>
#include <iostream>
#define GLOG_NO_ABBREVIATED_SEVERITIES
#include "ceres/ceres.h"
#include "ceres/rotation.h"

// Read a Bundle Adjustment in the Large dataset.
class BALProblem {
public:
    ~BALProblem() {
        delete[] point_index_;
        delete[] camera_index_;
        delete[] observations_;
        delete[] parameters_;
    }

    int num_observations() const { return num_observations_; }
    const double* observations() const { return observations_; }
    double* mutable_cameras() { return parameters_; }
    double* mutable_points() { return parameters_ + 9 * num_cameras_; }

    double* mutable_camera_for_observation(int i) {
        return mutable_cameras() + camera_index_[i] * 9;
    }
    double* mutable_point_for_observation(int i) {
        return mutable_points() + point_index_[i] * 3;
    }

    void WriteToFile(const std::string& filename) const {
        FILE* fptr = fopen(filename.c_str(), "w");

        if (fptr == nullptr) {
            LOG(FATAL) << "Error: unable to open file " << filename;
            return;
        };

        fprintf(fptr, "%d %d %d\n", num_cameras_, num_points_, num_observations_);

        for (int i = 0; i < num_observations_; ++i) {
            fprintf(fptr, "%d %d", camera_index_[i], point_index_[i]);
            for (int j = 0; j < 2; ++j) {
                fprintf(fptr, " %g", observations_[2 * i + j]);
            }
            fprintf(fptr, "\n");
        }

        for (int i = 0; i < num_cameras_; ++i) {
            double angleaxis[9];
            memcpy(angleaxis, parameters_ + 9 * i, 9 * sizeof(double));
            
            for (double coeff : angleaxis) {
                fprintf(fptr, "%.16g\n", coeff);
            }
        }
        const double* points = parameters_ + 9 * num_cameras_;
        for (int i = 0; i < num_points_; ++i) {
            const double* point = points + i * 3;
            for (int j = 0; j < 3; ++j) {
                fprintf(fptr, "%.16g\n", point[j]);
            }
        }
        fclose(fptr);
    }

    bool LoadFile(const char* filename) {
        FILE* fptr = fopen(filename, "r");
        if (fptr == nullptr) {
            return false;
        };

        FscanfOrDie(fptr, "%d", &num_cameras_);
        FscanfOrDie(fptr, "%d", &num_points_);
        FscanfOrDie(fptr, "%d", &num_observations_);

        point_index_ = new int[num_observations_];
        camera_index_ = new int[num_observations_];
        observations_ = new double[2 * num_observations_];

        num_parameters_ = 9 * num_cameras_ + 3 * num_points_;
        std::cout << 9 * num_cameras_ << "\n";
        std::cout << 3 * num_points_ << "\n";
        parameters_ = new double[num_parameters_];

        for (int i = 0; i < num_observations_; ++i) {
            FscanfOrDie(fptr, "%d", camera_index_ + i);
            FscanfOrDie(fptr, "%d", point_index_ + i);
            for (int j = 0; j < 2; ++j) {
                FscanfOrDie(fptr, "%lf", observations_ + 2 * i + j);
            }
        }
        std::cout << num_parameters_ << "\n";
        for (int i = 0; i < num_parameters_; ++i) {
            FscanfOrDie(fptr, "%lf", parameters_ + i);
        }
        return true;
    }

private:
    template <typename T>
    void FscanfOrDie(FILE* fptr, const char* format, T* value) {
        int num_scanned = fscanf(fptr, format, value);
        if (num_scanned != 1) {
            LOG(FATAL) << "Invalid UW data file.";
        }
    }

    int num_cameras_;
    int num_points_;
    int num_observations_;
    int num_parameters_;

    int* point_index_;
    int* camera_index_;
    double* observations_;
    double* parameters_;
};

// Templated pinhole camera model for used with Ceres.  The camera is
// parameterized using 9 parameters: 3 for rotation, 3 for translation, 1 for
// focal length and 2 for radial distortion. The principal point is not modeled
// (i.e. it is assumed be located at the image center).
struct SnavelyReprojectionError {
    SnavelyReprojectionError(double observed_x, double observed_y)
        : observed_x(observed_x), observed_y(observed_y) {}
    template <typename T>
    
    bool operator()(const T* const camera,
        const T* const point,
        T* residuals) const {

        T predicted3d[3];
        //matrix multiplication
        predicted3d[0] = point[0] * camera[0] + point[1] * camera[1] + point[2] * camera[2];
        predicted3d[1] = point[0] * camera[3] + point[1] * camera[4] + point[2] * camera[5];
        predicted3d[2] = point[0] * camera[6] + point[1] * camera[7] + point[2] * camera[8];

        // Compute back to planar vector
        T predicted_x = predicted3d[0] / predicted3d[2];
        T predicted_y = predicted3d[1] / predicted3d[2];

        // The error is the difference between the predicted and observed position.
        residuals[0] = predicted_x - observed_x;
        residuals[1] = predicted_y - observed_y;

        return true;
    }

    // Factory to hide the construction of the CostFunction object from
    // the client code.
    static ceres::CostFunction* Create(const double observed_x,
        const double observed_y) {
        return (new ceres::AutoDiffCostFunction<SnavelyReprojectionError, 2, 9, 3>(
            new SnavelyReprojectionError(observed_x, observed_y)));
    }

    double observed_x;
    double observed_y;
};

int main(int argc, char** argv) {
    google::InitGoogleLogging(argv[0]);

    BALProblem bal_problem;
    char filename[] = "problem_avgrid.txt";
    if (!bal_problem.LoadFile(filename)) {
        std::cerr << "ERROR: unable to open file " << filename << "\n";
        return 1;
    }
    std::cout << "File loaded";
    const double* observations = bal_problem.observations();

    // Create residuals for each observation in the bundle adjustment problem. The
    // parameters for cameras and points are added automatically.
    ceres::Problem problem;
    for (int i = 0; i < bal_problem.num_observations(); ++i) {
        // Each Residual block takes a point and a camera as input and outputs a 2
        // dimensional residual. Internally, the cost function stores the observed
        // image location and compares the reprojection against the observation.
        if (i % 1000 == 0) {
            std::cout << ".";
        }
        ceres::CostFunction* cost_function = SnavelyReprojectionError::Create(
            observations[2 * i + 0], observations[2 * i + 1]);
        problem.AddResidualBlock(cost_function,
            nullptr /* squared loss */,
            bal_problem.mutable_camera_for_observation(i),
            bal_problem.mutable_point_for_observation(i));
    }
    std::cout << "\nAdding done" << "\n";
    // Make Ceres automatically detect the bundle structure. Note that the
    // standard solver, SPARSE_NORMAL_CHOLESKY, also works fine but it is slower
    // for standard bundle adjustment problems.
    ceres::Solver::Options options;
    options.linear_solver_type = ceres::DENSE_SCHUR;
    options.minimizer_progress_to_stdout = true;

    ceres::Solver::Summary summary;
    std::cout << "Solve..." << "\n";
    ceres::Solve(options, &problem, &summary);
    std::cout << summary.FullReport() << "\n";
    bal_problem.WriteToFile("problem_avgrid_solved.txt");
    return 0;
}
