/*
  Copyright (c) 2012-2022 Carsten Burstedde, Donna Calhoun, Scott Aiton
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

#include "swirl_user.h"

#include "../all/advection_user.h"

#include <fclaw2d_rays.h>
#include <math.h>


typedef struct point
{
    double x;
    double y;
} point_t;


typedef enum 
{
    SWIRL_RAY_LINE,
    SWIRL_RAY_CIRCLE,
    SWIRL_RAY_TYPE_LAST
} swirl_ray_type_t;

typedef struct swirl_ray
{
    swirl_ray_type_t rtype;
    double xy[2];
    union 
    {
        struct 
        {
            double vec[2];
        } line;
        struct 
        {
            double radius;
        } circle;
    } r;
} swirl_ray_t;


static
int point_in_quad(point_t p0, point_t pll, point_t pur)
{
    int intx = (pll.x <= p0.x) && (p0.x <= pur.x);
    int inty = (pll.y <= p0.y) && (p0.y <= pur.y);

    int found = (intx != 0) && (inty != 0);
    return found;
}

static
double distance(point_t p0, point_t p1)
{
    double dx = p0.x - p1.x;
    double dy = p0.y - p1.y;
    double d = sqrt(dx*dx + dy*dy);
    return d;
}

static
int segment_intersect(point_t p0, point_t p1, 
                      point_t q0, point_t q1,
                      point_t *r)
{
    /* Find the intersection of two line segments.  */
    double a11 = p1.x - p0.x;
    double a21 = p1.y - p0.y;
    double a12 = -(q1.x - q0.x);
    double a22 = -(q1.y - q0.y);

    point_t b = {q0.x - p0.x, q0.y - p0.y};

    /* Compute determinant of A */
    double det = a22*a11 - a12*a21;
    int found_intersection = 0;
    if (det == 0)
    {
        found_intersection = 0;
        return 0;
    }

    double s,t;
    s = (a22*b.x - a12*b.y)/det;
    t = (-a21*b.x + a11*b.y)/det;

    if ((0 <= s && s <= 1) && (0 <= t && t <= 1))
        found_intersection = 1;

    r->x = q0.x + t*(q1.x - q0.x);
    r->y = q0.y + t*(q1.y - q0.y);

    return found_intersection;
}


int swirl_intersect_ray (fclaw2d_domain_t *domain, 
                         fclaw2d_patch_t * patch,
                         int blockno, 
                         int patchno, 
                         void *ray, 
                         double *integral)
{
  /* assert that ray is a valid swirl_ray_t */
  fclaw2d_ray_t *fclaw_ray = (fclaw2d_ray_t *) ray;  

  int id;
  swirl_ray_t *swirl_ray = (swirl_ray_t*) fclaw2d_ray_get_ray(fclaw_ray,&id);
  FCLAW_ASSERT(swirl_ray != NULL);
  FCLAW_ASSERT(swirl_ray->rtype == SWIRL_RAY_LINE); /* Circles not there yet. */

  if (patchno >= 0) 
  {
     /* We are at a leaf and the patch is a valid patch of the domain.
     * Based on the patch, the domain, the blockno and the information stored
     * in the swirl_ray_t we defined, we now have to set *integral to be the
     * contribution of this ray-patch combination to the ray integral.
     * We should return 1 (even though a leaf return value is ignored). */

    /* This is a dummy example.  We add the ray's x component for each patch.
       Truly, this example must be updated to compute the exact ray integral. */
    // *integral = swirl_ray->r.line.vec[0];

    /* DAC : Updated to consider intersection of ray with quadrant.  Contribution to the 
        integral is the length of the ray segment that in the quad. 

        Next step : consider parameterized curve.  */

    /* Get data on current patch */
    int mx,my,mbc;
    double xlower,ylower,dx,dy;    
    fclaw2d_clawpatch_grid_data(NULL,patch,&mx,&my,&mbc,
                                &xlower,&ylower,&dx,&dy);


    if (swirl_ray->rtype == SWIRL_RAY_LINE)
    {
        /* Check to see if line segment intersections one of four edges. */
        point_t p0 = {swirl_ray->xy[0], swirl_ray->xy[1]};
        point_t p1 = {p0.x + swirl_ray->r.line.vec[0],
                      p0.y + swirl_ray->r.line.vec[1]};

        double qx[5] = {xlower, xlower+dx*mx, xlower+dx*mx, xlower, xlower};
        double qy[5] = {ylower, ylower, ylower+dy*my, ylower+dy*my, ylower};

        point_t r;
        int istart = -1, iend = -1;
        point_t r0, r1;        
        for(int i = 0; i < 4; i++)
        {
            point_t q0 = {qx[i],qy[i]};
            point_t q1 = {qx[i+1],qy[i+1]};

            int found = segment_intersect(p0,p1,q0,q1,&r);
            if (found != 0)
            {
                if (istart < 0)
                {
                    istart = i;
                    r0 = r;
                }
                else
                {
                    iend = i;
                    r1 = r;
                    break;
                }
            }
        }
        /* Four cases */
        int found_intersection = 0;
        point_t pstart, pend;
        if (istart < 0 && iend < 0)
        {
            /* No intersection found */
            //fclaw_global_essentialf("No intersection found\n");
            *integral = 0;
        }
        else if (istart >= 0 && iend >= 0)
        {
            /* Ray enters and exits quad */
            //fclaw_global_essentialf("Ray enters and exits quad\n");
            pstart = r0;
            pend = r1;
            found_intersection = 1;
        }
        else
        {
            /* Ray starts or ends in quad */
            point_t pll = {xlower,ylower};
            point_t pur = {xlower+1,ylower+1};
            if (point_in_quad(p0,pll,pur) != 0)
            {
                //fclaw_global_essentialf("Ray starts in quad and exits\n");
                pstart = p0;
                pend = r0;
            }
            else if (point_in_quad(p1,pll,pur) != 0)
            {
                //fclaw_global_essentialf("Ray starts outside quad and enters\n");
                pstart = r0;
                pend = p1;
            }
            found_intersection = 1;
        }
        if (found_intersection != 0)
        {
            /* This could be replaced by an integral along a curve in the patch */
            *integral = distance(pstart,pend);
        }
    }  /* end of ray type line */
    return 1;
  } 
  else 
  {
    /* We are not at a leaf and the patch is an artificial patch containing all
     * standard patch information except for the pointer to the next patch and
     * user-data of any kind. Only the FCLAW2D_PATCH_CHILDID and the
     * FCLAW2D_PATCH_ON_BLOCK_FACE_* flags are set.
     * Based on this, we now can run a test to check if the ray and the patch
     * intersect.
     * We return 0 if we are certain that the ray does not intersect any
     * descendant of this patch.
     * We return 1 if the test concludes that the ray may intersect the patch.
     * This test may be overinclusive / false positive to optimize for speed.
     *
     * The purpose of this test is to remove irrelevant ancestor
     * patch-ray-combinations early on to avoid unnecessary computations.
     * We do not need to assign to the integral value for ancestor patches. */

    /* This is a dummy example.  Truly, implement a fast and over-inclusive test
     * to see if this ray may possibly intersect the patch and return the answer. */
    return 1;
  }
}


static int nlines = 3;

#if 0
sc_array_t * swirl_rays_new (void)
{
    swirl_ray_t *ray;
    sc_array_t  *a = sc_array_new (sizeof (fclaw2d_ray_t));

    /* add a couple straight rays */
    for (int i = 0; i < nlines; ++i) 
    {
        ray = (swirl_ray_t*) FCLAW_ALLOC(swirl_ray_t,1);
        ray->rtype = SWIRL_RAY_LINE;
        ray->xy[0] = 0.;
        ray->xy[1] = 0.;
        ray->r.line.vec[0] = cos (i * M_PI / nlines);
        ray->r.line.vec[1] = sin (i * M_PI / nlines);

        fclaw2d_ray_t *fclaw_ray = (fclaw2d_ray_t *) sc_array_push (a);
        fclaw2d_ray_set_ray(NULL,fclaw_ray,i, ray);
    }

    /* add no circles yet */
    return a;
}
#endif



/* Virtual function for setting rays */
static
void swirl_allocate_and_define_rays(fclaw2d_global_t *glob, 
                                    fclaw2d_ray_t** rays, 
                                    int* num_rays)
{
    *num_rays = nlines;

    /* We let the user allocate an array of rays, although what is inside the 
       generic ray type is left opaque. This is destroy in matching FREE,
       below. */
    *rays = (fclaw2d_ray_t*) FCLAW_ALLOC(fclaw2d_ray_t,*num_rays);
    fclaw2d_ray_t *ray_vec = *rays;
    for (int i = 0; i < nlines; ++i) 
    {
        //fclaw_global_essentialf("ray_initialize : Setting up ray %d : \n",i);
        swirl_ray_t *sr = (swirl_ray_t*) FCLAW_ALLOC(swirl_ray_t,1);
        sr->rtype = SWIRL_RAY_LINE;
        sr->xy[0] = 0.;
        sr->xy[1] = 0.;

#if 0
        sr->r.line.vec[0] = cos (i * M_PI / (nlines-1));
        sr->r.line.vec[1] = sin (i * M_PI / (nlines-1));
#else        
        /* End points are on a semi-circle in x>0,y>0 quad */
        FCLAW_ASSERT(nlines >= 2);
        double R = 0.25;
        double dth = M_PI/(2*(nlines-1));
        sr->r.line.vec[0] = R*cos (i * dth);
        sr->r.line.vec[1] = R*sin (i * dth);
#endif        

        fclaw2d_ray_t *ray = &ray_vec[i];
        int id = i + 1;
        fclaw2d_ray_set_ray(ray,id, sr);
    }
}


static
void swirl_deallocate_rays(fclaw2d_global_t *glob, 
                           fclaw2d_ray_t** rays, 
                           int* num_rays)
{
    fclaw2d_ray_t *ray_vec = *rays;
    for(int i = 0; i < *num_rays; i++)
    {
        /* Retrieve rays set above and deallocate them */
        int id;
        fclaw2d_ray_t *ray = &ray_vec[i];
        swirl_ray_t *rs = (swirl_ray_t*) fclaw2d_ray_get_ray(ray,&id);
        FCLAW_ASSERT(rs != NULL);
        FCLAW_FREE(rs);
        rs = NULL;
    }
    /* Match FCLAW_ALLOC, above */
    FCLAW_FREE(*rays);  
    *num_rays = 0;  
    *rays = NULL;
}

void swirl_initialize_rays(fclaw2d_global_t* glob)
{
    /* Set up rays */
    fclaw2d_ray_vtable_t* rays_vt = fclaw2d_ray_vt(); 

    rays_vt->allocate_and_define = swirl_allocate_and_define_rays;
    rays_vt->deallocate = swirl_deallocate_rays;

    rays_vt->integrate = swirl_intersect_ray;
}


sc_array_t * swirl_integrals_new(void)
{
    return sc_array_new_count (sizeof (double), nlines);
}