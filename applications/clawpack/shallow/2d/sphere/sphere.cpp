/*
Copyright (c) 2012-2023 Carsten Burstedde, Donna Calhoun, Scott Aiton
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

#include "sphere_user.h"

#include <fclaw2d_clawpatch_options.h>
#include <fclaw2d_clawpatch.h>

#include <fc2d_clawpack46_options.h>
#include <fc2d_clawpack5_options.h>

#include <fc2d_clawpack46.h>
#include <fc2d_clawpack5.h>


static
void create_domain(fclaw2d_global_t *glob)
{
    const fclaw_options_t* fclaw_opt = fclaw2d_get_options(glob);
    double rotate[2];
    rotate[0] = fclaw_opt->phi;
    rotate[1] = fclaw_opt->theta;
    int mi = fclaw_opt->mi;
    int mj = fclaw_opt->mj;
    int a = fclaw_opt->periodic_x;
    int b = fclaw_opt->periodic_y;


    /* Mapped, multi-block domain */
    fclaw2d_domain_t *domain;
    fclaw2d_map_context_t  *cont = NULL, *brick=NULL;

    const fclaw2d_clawpatch_options_t *clawpatch_opt = 
        fclaw2d_clawpatch_get_options(glob);

    user_options_t *user_opt = sphere_get_options(glob);
    switch (user_opt->mapping) 
    {
    case 1:
        if (clawpatch_opt->mx*pow_int(2,fclaw_opt->minlevel) < 32)
        {
            fclaw_global_essentialf("The cubed-sphere mapping requires mx*2^minlevel >= 32\n");
            exit(0);
        }

        domain =
            fclaw2d_domain_new_cubedsphere(glob->mpicomm,
                                            fclaw_opt->minlevel);

        cont = fclaw2d_map_new_cubedsphere(fclaw_opt->scale, rotate);
        break;
    case 2:
        /* Create brick domain with periodicity */
        if (a != 0)
        {
            // Domain is periodic in x
            user_opt->longitude[0] = 0;
            user_opt->longitude[1] = 360;
        }

        domain =     
            fclaw2d_domain_new_brick(glob->mpicomm, mi, mj, a, b,
                                     fclaw_opt->minlevel);

        /* Create brick mapping */
        brick =
            fclaw2d_map_new_brick(domain, mi, mj, a, b);

        /* Create latlong mapping based on brick */
        cont = fclaw2d_map_new_latlong(brick,fclaw_opt->scale,
                                       rotate,
                                       user_opt->latitude, 
                                       user_opt->longitude,
                                       a,b);
        break;
    case 3:
        domain = fclaw2d_domain_new_twosphere(glob->mpicomm, 
                                              fclaw_opt->minlevel);

        cont = fclaw2d_map_new_pillowsphere (fclaw_opt->scale, rotate);
        break;
    default:
        SC_ABORT_NOT_REACHED ();
    }

    /* Store the domain in the glob */
    fclaw2d_global_store_domain(glob, domain);

    /* Store mapping in the glob */
    fclaw2d_global_store_map (glob, cont);            

    /* print out some info */
    fclaw2d_domain_list_levels(domain, FCLAW_VERBOSITY_ESSENTIAL);
    fclaw2d_domain_list_neighbors(domain, FCLAW_VERBOSITY_DEBUG);  
}


#if 0
static
void run_program(fclaw_app_t* app)
{
    /* ---------------------------------------------------------------
       Set domain data.
       --------------------------------------------------------------- */
    fclaw2d_domain_set_app (domain,app);

    you_can_safely_remove_this_call(domain);

    sphere_link_solvers(domain);

    fclaw_initialize(&domain);
    fclaw_run(&domain);
    fclaw_finalize(&domain);
}
#endif

static
void run_program(fclaw2d_global_t* glob)
{
    /* ---------------------------------------------------------------
       Set domain data.
       --------------------------------------------------------------- */
    fclaw2d_domain_data_new(glob->domain);

    const user_options_t *user_opt = sphere_get_options(glob);

    /* Initialize virtual table for ForestClaw */
    fclaw2d_vtables_initialize(glob);

    /* Initialize virtual tables for solvers */
    if (user_opt->claw_version == 4)
    {
        fc2d_clawpack46_solver_initialize(glob);
    }
    else if (user_opt->claw_version == 5)
    {
        fc2d_clawpack5_solver_initialize(glob);
    }

    sphere_link_solvers(glob);

    /* ---------------------------------------------------------------
       Run
       --------------------------------------------------------------- */

    fclaw2d_initialize(glob);
    fclaw2d_run(glob);
    fclaw2d_finalize(glob);
}


int
main (int argc, char **argv)
{
    fclaw_app_t *app = fclaw_app_new (&argc, &argv, NULL);

    /* Options */
    user_options_t              *user_opt;
    fclaw_options_t             *fclaw_opt;
    fclaw2d_clawpatch_options_t *clawpatch_opt;
    fc2d_clawpack46_options_t   *claw46_opt;
    fc2d_clawpack5_options_t    *claw5_opt;

    /* Create new options packages */
    fclaw_opt =                   fclaw_options_register(app,  NULL,        "fclaw_options.ini");
    clawpatch_opt =   fclaw2d_clawpatch_options_register(app, "clawpatch",  "fclaw_options.ini");
    claw46_opt =        fc2d_clawpack46_options_register(app, "clawpack46", "fclaw_options.ini");
    claw5_opt =          fc2d_clawpack5_options_register(app, "clawpack5",  "fclaw_options.ini");
    user_opt =                sphere_options_register(app,"fclaw_options.ini");

    /* Read configuration file(s) and command line, and process options */
    int first_arg;
    fclaw_exit_type_t vexit = 
        fclaw_app_options_parse (app, &first_arg,"fclaw_options.ini.used");

    /* Run the program */
    if (vexit < 2)
    {
        /* Options have been checked and are valid */

        /* Create global structure which stores the domain, timers, etc */
        int size, rank;
        sc_MPI_Comm mpicomm = fclaw_app_get_mpi_size_rank (app, &size, &rank);
        fclaw2d_global_t *glob = fclaw2d_global_new_comm (mpicomm, size, rank);

        /* Store option packages in glob */
        fclaw2d_options_store           (glob, fclaw_opt);
        fclaw2d_clawpatch_options_store (glob, clawpatch_opt);
        fc2d_clawpack46_options_store   (glob, claw46_opt);
        fc2d_clawpack5_options_store    (glob, claw5_opt);
        sphere_options_store            (glob, user_opt);

        /* Create domain and store domain in glob */
        create_domain(glob);

        run_program(glob);

        fclaw2d_global_destroy(glob);
    }

    fclaw_app_destroy (app);

    return 0;
}
