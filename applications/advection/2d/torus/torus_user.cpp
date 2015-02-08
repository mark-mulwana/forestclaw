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

#include "amr_includes.H"
#include "fc2d_clawpack46.H"
#include "torus_user.H"

#ifdef __cplusplus
extern "C"
{
#if 0
}
#endif
#endif

static const fc2d_clawpack46_vtable_t classic_user =
{
    setprob_,
    NULL,        /* bc2 */
    qinit_,      /* qinit */
    setaux_,     /* Setaux */
    NULL,        /* b4step2 */
    NULL,         /* src2 */
    rpn2_,
    rpt2_
};


void torus_link_solvers(fclaw2d_domain_t *domain)
{
    fclaw2d_solver_functions_t* sf = get_solver_functions(domain);
    sf->use_single_step_update = fclaw_true;
    sf->use_mol_update = fclaw_false;
    sf->f_patch_setup              = &torus_patch_setup;
    sf->f_patch_initialize         = &torus_qinit;
    sf->f_patch_single_step_update = &torus_update;

    /* Boundary conditions */
    sf->f_patch_physical_bc        = &fc2d_clawpack46_bc2;


    fclaw2d_regrid_functions_t *rf = get_regrid_functions(domain);
    rf->f_patch_tag4refinement = &torus_patch_tag4refinement;
    rf->f_patch_tag4coarsening = &torus_patch_tag4coarsening;

    fclaw2d_output_functions_t *of = get_output_functions(domain);
    of->f_patch_write_header = &torus_parallel_write_header;
    of->f_patch_write_output = &torus_parallel_write_output;

    fc2d_clawpack46_set_vtable(&classic_user);

    /* This is needed to get constructors for user data */
    fc2d_clawpack46_link_to_clawpatch();
}

void torus_problem_setup(fclaw2d_domain_t* domain)
{
    fc2d_clawpack46_setprob(domain);
}

void torus_patch_setup(fclaw2d_domain_t *domain,
                       fclaw2d_patch_t *this_patch,
                       int this_block_idx,
                       int this_patch_idx)
{
    /* ----------------------------------------------------------- */
    // Global parameters
    const amr_options_t *gparms = get_domain_parms(domain);
    if (!gparms->manifold)
    {
        fc2d_clawpack46_setaux(domain,this_patch,this_block_idx,this_patch_idx);
    }
    else
    {
        int mx = gparms->mx;
        int my = gparms->my;
        int mbc = gparms->mbc;

        ClawPatch *cp = get_clawpatch(this_patch);
        double xlower = cp->xlower();
        double ylower = cp->ylower();
        double dx = cp->dx();
        double dy = cp->dy();

        fc2d_clawpack46_define_auxarray(domain,cp);

        double *aux;
        int maux;
        fc2d_clawpack46_get_auxarray(domain,cp,&aux,&maux);

        double *xp = cp->xp();
        double *yp = cp->yp();
        double *zp = cp->zp();
        double *xd = cp->xd();
        double *yd = cp->yd();
        double *zd = cp->zd();
        double *xnormals = cp->xface_normals();
        double *ynormals = cp->yface_normals();
        double *edge_lengths = cp->edge_lengths();
        double *area = cp->area();

        setaux_manifold_(mbc,mx,my,this_block_idx,xlower,ylower,dx,dy,
                         maux,aux,xp,yp,zp,xd,yd,zd,xnormals,ynormals,
                         edge_lengths,area);
    }
}

void torus_qinit(fclaw2d_domain_t *domain,
                 fclaw2d_patch_t *this_patch,
                 int this_block_idx,
                 int this_patch_idx)
{

    fc2d_clawpack46_qinit(domain,this_patch,this_block_idx,this_patch_idx);
}

void torus_patch_physical_bc(fclaw2d_domain *domain,
                                    fclaw2d_patch_t *this_patch,
                                    int this_block_idx,
                                    int this_patch_idx,
                                    double t,
                                    double dt,
                                    fclaw_bool intersects_bc[])
{
    // The torus has no physical boundaries
}



double torus_update(fclaw2d_domain_t *domain,
                         fclaw2d_patch_t *this_patch,
                         int this_block_idx,
                         int this_patch_idx,
                         double t,
                         double dt)
{
    double maxcfl = fc2d_clawpack46_step2(domain,this_patch,
                                          this_block_idx,
                                          this_patch_idx,t,dt);

    return maxcfl;
}

/* -----------------------------------------------------------------
   Default routine for tagging patches for refinement and coarsening
   ----------------------------------------------------------------- */
fclaw_bool torus_patch_tag4refinement(fclaw2d_domain_t *domain,
                                      fclaw2d_patch_t *this_patch,
                                      int this_block_idx, int this_patch_idx,
                                      int initflag)
{
    /* ----------------------------------------------------------- */
    // Global parameters
    const amr_options_t *gparms = get_domain_parms(domain);
    int mx = gparms->mx;
    int my = gparms->my;
    int mbc = gparms->mbc;
    int meqn = gparms->meqn;

    /* ----------------------------------------------------------- */
    // Patch specific parameters
    ClawPatch *cp = get_clawpatch(this_patch);
    double xlower = cp->xlower();
    double ylower = cp->ylower();
    double dx = cp->dx();
    double dy = cp->dy();

    /* ------------------------------------------------------------ */
    // Pointers needed to pass to Fortran
    double* q = cp->q();

    int tag_patch = 0;  // == 0 or 1

    torus_tag4refinement_(mx,my,mbc,meqn,xlower,ylower,dx,dy,q,initflag,
                           this_block_idx,tag_patch);
    return tag_patch == 1;
}

fclaw_bool torus_patch_tag4coarsening(fclaw2d_domain_t *domain,
                                             fclaw2d_patch_t *this_patch,
                                             int blockno_idx,
                                             int patchno)
{
    /* ----------------------------------------------------------- */
    // Global parameters
    const amr_options_t *gparms = get_domain_parms(domain);
    int mx = gparms->mx;
    int my = gparms->my;
    int mbc = gparms->mbc;
    int meqn = gparms->meqn;

    /* ----------------------------------------------------------- */
    // Patch specific parameters
    ClawPatch *cp = get_clawpatch(this_patch);
    double xlower = cp->xlower();
    double ylower = cp->ylower();
    double dx = cp->dx();
    double dy = cp->dy();

    /* ------------------------------------------------------------ */
    // Pointers needed to pass to Fortran
    double* q = cp->q();

    int tag_patch;  // == 0 or 1
    torus_tag4coarsening_(mx,my,mbc,meqn,xlower,ylower,dx,dy,q,tag_patch);
    return tag_patch == 0;
}

void torus_parallel_write_header(fclaw2d_domain_t* domain, int iframe, int ngrids)
{
    const amr_options_t *gparms = get_domain_parms(domain);
    double time = get_domain_time(domain);

    fclaw_global_essentialf("Matlab output Frame %d  at time %16.8e\n\n",iframe,time);

    /* Increase the number of fields by 1 so we can printout the mpi rank */
    int mfields = gparms->meqn;
    int maux = 0;
    torus_write_tfile_(iframe,time,mfields,ngrids,maux);

    /* This opens file 'fort.qXXXX' for replace
       (where XXXX = <zero padding><iframe>, e.g. 0001, 0010, 0114),
       and closes the file. */
    new_qfile_(iframe);
}


void torus_parallel_write_output(fclaw2d_domain_t *domain, fclaw2d_patch_t *this_patch,
                                  int this_block_idx, int this_patch_idx,
                                  int iframe,int num,int level)
{
    /* ----------------------------------------------------------- */
    // Global parameters
    const amr_options_t *gparms = get_domain_parms(domain);
    int mx = gparms->mx;
    int my = gparms->my;
    int mbc = gparms->mbc;
    int meqn = gparms->meqn;

    /* ----------------------------------------------------------- */
    // Patch specific parameters
    ClawPatch *cp = get_clawpatch(this_patch);
    double xlower = cp->xlower();
    double ylower = cp->ylower();
    double dx = cp->dx();
    double dy = cp->dy();

    /* ------------------------------------------------------------ */
    // Pointers needed to pass to Fortran
    double* q = cp->q();

    // Other input arguments
    int maxmx = mx;
    int maxmy = my;

    /* ------------------------------------------------------------- */
    int matlab_level = level;

    int mpirank = domain->mpirank;
    /* This opens a file for append and writes in the 'clawout' style. */
    torus_write_qfile_(maxmx,maxmy,meqn,mbc,mx,my,xlower,ylower,dx,dy,q,
                        iframe,num,matlab_level,this_block_idx,mpirank);
}



#ifdef __cplusplus
#if 0
{
#endif
}
#endif
