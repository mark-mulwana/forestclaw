/*
Copyright (c) 2012 Carsten Burstedde, Donna Calhoun
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

#ifndef CYLINDER_USER_H
#define CYLINDER_USER_H

#include <fclaw2d_include_all.h>

#ifdef __cplusplus
extern "C"
{
#if 0
}
#endif
#endif

#if 0
#endif

/* --------------------------
   Headers for both versions
   -------------------------- */

typedef struct user_options
{
    int example;
    int initial_condition;  /* Smooth or non-smooth */
    int refine_pattern;

    int exact_metric;

    /* Radius and height of cylinder */
    double R;
    double H;

    /* Radius and center of initial disk */
    double xc0;
    double yc0;
    double r0;

    double revs_per_s;     /* radial speed */
    double v_speed;             /* Vertical speed */

    int mapping;   /* 0 - cylinder;  1 - latlong */

    int claw_version;

    int is_registered;
}
user_options_t;

#define CYLINDER_SETPROB FCLAW_F77_FUNC(cylinder_setprob,CYLINDER_SETPROB)
void CYLINDER_SETPROB();

#define COMPUTE_EXACT FCLAW_F77_FUNC(compute_exact, COMPUTE_EXACT)
void COMPUTE_EXACT();



void cylinder_link_solvers(fclaw2d_global_t *glob);

user_options_t* cylinder_options_register (fclaw_app_t * app,
                                       const char *configfile);


void cylinder_options_store (fclaw2d_global_t* glob, user_options_t* user);

const user_options_t* cylinder_get_options(fclaw2d_global_t* glob);

fclaw2d_map_context_t *
    fclaw2d_map_new_cylinder (fclaw2d_map_context_t* brick, const double scale[], 
                              int mapping);


/* --------------------------
   Mapping headers - cylinder
   -------------------------- */

#define CYLINDER_COMPUTE_AREA FCLAW_F77_FUNC(cylinder_compute_area, \
                                             CYLINDER_COMPUTE_AREA)

void CYLINDER_COMPUTE_AREA(int *mx,int *my,int *mbc,double *dx, double *dy, 
                           double *xlower, double *ylower, int *blockno, 
                           int *maxlevel, int *level, double area[]);


#define CYLINDER_COMPUTE_TANGENTS FCLAW_F77_FUNC(cylinder_compute_tangents, \
                                                 CYLINDER_COMPUTE_TANGENTS)

void CYLINDER_COMPUTE_TANGENTS(int* mx,int* my, int* mbc,double* dx, double* dy, 
                               int* level, double *xd, double *yd, double* zd,
                               double *xtangents,double* ytangents,
                               double* edgelengths);


#define CYLINDER_COMPUTE_NORMALS FCLAW_F77_FUNC(cylinder_compute_normals, \
                                              CYLINDER_COMPUTE_NORMALS)

void CYLINDER_COMPUTE_NORMALS(int* mx,int* my,int* mbc,
                              double xp[], double yp[], double zp[],
                              double xd[], double yd[], double zd[],
                              double xnormals[], double ynormals[]);

/* --------------------------
   Mapping headers - LATLONG
   -------------------------- */

#define LATLONG_COMPUTE_AREA FCLAW_F77_FUNC(latlong_compute_area, \
                                             LATLONG_COMPUTE_AREA)

void LATLONG_COMPUTE_AREA(int *mx,int *my,int *mbc,double *dx, double *dy, 
                           double *xlower, double *ylower, int *blockno, 
                           int *maxlevel, int *level, double area[]);


#define LATLONG_COMPUTE_TANGENTS FCLAW_F77_FUNC(latlong_compute_tangents, \
                                                 LATLONG_COMPUTE_TANGENTS)

void LATLONG_COMPUTE_TANGENTS(int* mx,int* my, int* mbc,double* dx, double* dy, 
                               int* level, double *xd, double *yd, double* zd,
                               double *xtangents,double* ytangents,
                               double* edgelengths);


#define LATLONG_COMPUTE_NORMALS FCLAW_F77_FUNC(latlong_compute_normals, \
                                              LATLONG_COMPUTE_NORMALS)

void LATLONG_COMPUTE_NORMALS(int* mx,int* my,int* mbc,
                             double xp[], double yp[], double zp[],
                             double xd[], double yd[], double zd[],
                             double xnormals[], double ynormals[]);


/* ----------------------
   Clawpack 4.6 headers
   ---------------------- */
#define CYLINDER46_COMPUTE_ERROR FCLAW_F77_FUNC(cylinder46_compute_error,CYLINDER46_COMPUTE_ERROR)

void CYLINDER46_COMPUTE_ERROR(int* blockno, int *mx, int *my, int* mbc, int* meqn,
                           double *dx, double *dy, double *xlower,
                           double *ylower, double *t, double q[],
                           double error[], double soln[]);

#define CYLINDER_SETAUX FCLAW_F77_FUNC(cylinder_setaux,CYLINDER_SETAUX)

void CYLINDER_SETAUX(const int* blockno, const int* mx, const int* my,
                   const int* mbc, const double* xlower, const double* ylower,
                   const double* dx, const double* dy, 
                   double area[],double edgelengths[],
                   double xp[], double yp[], double zp[],
                   double aux[],const int* maux);


#define CYLINDER_SET_VELOCITIES FCLAW_F77_FUNC(cylinder_set_velocities, \
                                             CYLINDER_SET_VELOCITIES)

void CYLINDER_SET_VELOCITIES(const int* blockno, const int* mx, const int* my,
                   const int* mbc, const double* dx, const double* dy,
                   const double* xlower, const double* ylower,
                   const double *t, double xnormals[],double ynormals[],
                   double surfnormals[], double aux[],const int* maux);



#define  CYLINDER46_FORT_WRITE_FILE FCLAW_F77_FUNC(cylinder46_fort_write_file,  \
                                                CYLINDER46_FORT_WRITE_FILE)
void     CYLINDER46_FORT_WRITE_FILE(char* matname1,
                                 int* mx,        int* my,
                                 int* meqn,      int* mbc,
                                 double* xlower, double* ylower,
                                 double* dx,     double* dy,
                                 double q[],     double error[], double soln[],
                                 double *time,
                                 int* patch_num, int* level,
                                 int* blockno,   int* mpirank);

#define CYLINDER46_FORT_HEADER_ASCII \
         FCLAW_F77_FUNC(cylinder46_fort_header_ascii, \
                        CYLINDER46_FORT_HEADER_ASCII)
void CYLINDER46_FORT_HEADER_ASCII(char* matname1, char* matname2,
                               double* time, int* meqn, int* maux, 
                               int* ngrids);


#define CYLINDER_TAG4REFINEMENT FCLAW_F77_FUNC(cylinder_tag4refinement, \
                                              CYLINDER_TAG4REFINEMENT)
void  CYLINDER_TAG4REFINEMENT(const int* mx,const int* my,
                             const int* mbc,const int* meqn,
                             const double* xlower, const double* ylower,
                             const double* dx, const double* dy,
                             const int* blockno,
                             double q[], const double* tag_threshold,
                             const int* init_flag,
                             int* tag_patch);

#define  CYLINDER_TAG4COARSENING FCLAW_F77_FUNC(cylinder_tag4coarsening, \
                                              CYLINDER_TAG4COARSENING)
void  CYLINDER_TAG4COARSENING(const int* mx, const int* my,
                             const int* mbc, const int* meqn,
                             const double* xlower, const double* ylower,
                             const double* dx, const double* dy,
                             const int* blockno,
                             double q0[],double q1[],
                             double q2[],double q3[],
                             const double* tag_threshold,
                             int* tag_patch);



#define RPN2CONS_FW_MANIFOLD FCLAW_F77_FUNC(rpn2cons_fw_manifold, RPN2CONS_FW_MANIFOLD)
void RPN2CONS_FW_MANIFOLD(const int* ixy, const int* maxm, const int* meqn, 
                          const int* mwaves,
                          const int* mbc, const int* mx, double ql[], double qr[],
                          double auxl[], double auxr[], double fwave[],
                          double s[], double amdq[], double apdq[]);


#define RPT2CONS_MANIFOLD FCLAW_F77_FUNC(rpt2cons_manifold, RPT2CONS_MANIFOLD)
void RPT2CONS_MANIFOLD(const int* ixy, const int* maxm, const int* meqn, const int* mwaves,
                       const int* mbc, const int* mx, double ql[], double qr[],
                       double aux1[], double aux2[], double aux3[], const int* imp,
                       double dsdq[], double bmasdq[], double bpasdq[]);


#define RPN2_CONS_UPDATE_MANIFOLD FCLAW_F77_FUNC(rpn2_cons_update_manifold, \
                                                 RPN2_CONS_UPDATE_MANIFOLD)

void RPN2_CONS_UPDATE_MANIFOLD(const int* meqn, const int* maux, const int* idir,
                               const int* iface, double q[], 
                               double aux_center[], double aux_edge[],
                               double flux[]);

#define RPN2_CONS_UPDATE_ZERO FCLAW_F77_FUNC(rpn2_cons_update_zero, \
                                             RPN2_CONS_UPDATE_ZERO)

void RPN2_CONS_UPDATE_ZERO(const int* meqn, const int* maux, const int* idir,
                           const int* iface,
                           double q[], double aux_center[], double aux_edge[],
                           double flux[]);


/* ----------------------
   Clawpack 5.x headers
   ---------------------- */

#if 0
#define CYLINDER5_COMPUTE_ERROR FCLAW_F77_FUNC(cylinder5_compute_erCYLINDER5_COMPUTE_ERROR)

voiCYLINDER5_COMPUTE_ERROR(int* blockno, int *mx, int *my, int* mbc, int* meqn,
                          double *dx, double *dy, double *xlower,
                          double *ylower, double *t, double q[],
                          double error[]);

#defineCYLINDER5_SETAUX  FCLAW_F77_FUNC(cylinder5_setaux, CYLINDER5_SETAUX)
voiCYLINDER5_SETAUX(const int* mbc,
                   const int* mx, const int* my,
                   const double* xlower, const double* ylower,
                   const double* dx, const double* dy,
                   const int* maux, double aux[]);


#defineCYLINDER5_FORT_WRITE_FILE FCLAW_F77_FUNC(cylinder5_fort_write_file,  \
                                               CYLINDER5_FORT_WRITE_FILE)
void   CYLINDER5_FORT_WRITE_FILE(char* matname1,
                                int* mx,        int* my,
                                int* meqn,      int* mbc,
                                double* xlower, double* ylower,
                                double* dx,     double* dy,
                                double q[],     double error[],
                                int* patch_num, int* level,
                                int* blockno,   int* mpirank);

#defineCYLINDER5_TAG4REFINEMENT FCLAW_F77_FUNC(cylinder5_tag4refinement, \
                                           CYLINDER5_TAG4REFINEMENT)
voiCYLINDER5_TAG4REFINEMENT(const int* mx,const int* my,
                             const int* mbc,const int* meqn,
                             const double* xlower, const double* ylower,
                             const double* dx, const double* dy,
                             const int* blockno,
                             double q[],
                             const double* tag_threshold,
                             const int* init_flag,
                             int* tag_patch);

#defineCYLINDER5_TAG4COARSENING FCLAW_F77_FUNC(cylinder5_tag4coarsening, \
                                           CYLINDER5_TAG4COARSENING)
voiCYLINDER5_TAG4COARSENING(const int* mx, const int* my,
                             const int* mbc, const int* meqn,
                             const double* xlower, const double* ylower,
                             const double* dx, const double* dy,
                             const int* blockno,
                             double q0[],double q1[],
                             double q2[],double q3[],
                             const double* tag_threshold,
                             int* tag_patch);
#endif



#ifdef __cplusplus
#if 0
{
#endif
}
#endif

#endif /* CYLINDER_USER_H */
