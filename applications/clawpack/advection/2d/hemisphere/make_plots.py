
""" 
Plot using Clawpack's visclaw graphics.  This file can be run as ; 

    % python plot_filament.py

To learn more about visclaw graphics, see www.clawpack.org
    
""" 
import numpy as np
alpha = 0.4

def set_blocknumber(current_data):
    global blocknumber
    blocknumber = current_data.patch.block_number
    return current_data.q[0,:,:]

def mapc2p_bilinear(xc, yc, center):

    # Initialize the quad array
    quad = np.zeros((2, 2, 2))
    quad[0, 0, :] = [0, 0]
    quad[1, 0, :] = [1, 0]
    quad[0, 1, :] = [0, 1]
    quad[1, 1, :] = [1, 1]
    
    # Set 's' based on block number
    if blocknumber == 0:
        s = np.array([[-1], [-1]])
    elif blocknumber == 1:
        s = np.array([[0], [-1]])
    elif blocknumber == 2:
        s = np.array([[-1], [0]])
    elif blocknumber == 3:
        s = np.array([[0], [0]])
    else:
        raise ValueError("Invalid block number")

    # Apply s to the quad coordinates
    for i in range(2):
        for j in range(2):
            quad[i, j, 0] += s[0]
            quad[i, j, 1] += s[1]

    # Adjust quad based on block number and center should be an array
    if blocknumber == 0:
        quad[1, 1, :] = center
    elif blocknumber == 1:
        quad[0, 1, :] = center
    elif blocknumber == 2:
        quad[1, 0, :] = center
    elif blocknumber == 3:
        quad[0, 0, :] = center
    else:
        raise ValueError("Invalid block number")

    # Initialize xp,yp and zp arrays
    xp = np.zeros_like(xc)
    yp = np.zeros_like(yc)
    zp = np.zeros_like(xc)  

    m, n = xc.shape

    # Compute xp and yp basing on the bilinear transformation
    for i in range(m):
        for j in range(n):
            a00 = np.zeros(2)
            a01 = np.zeros(2)
            a10 = np.zeros(2)
            a11 = np.zeros(2)

            for k in range(2):
                a00[k] = quad[0, 0, k]  
                a01[k] = quad[1, 0, k] - quad[0, 0, k]  
                a10[k] = quad[0, 1, k] - quad[0, 0, k]  
                a11[k] = quad[1, 1, k] - quad[1, 0, k] - quad[0, 1, k] + quad[0, 0, k]  

        
        xp[i, j] = a00[0] + a01[0] * xc[i, j] + a10[0] * yc[i, j] + a11[0] * xc[i, j] * yc[i, j]
        yp[i, j] = a00[1] + a01[1] * xc[i, j] + a10[1] * yc[i, j] + a11[1] * xc[i, j] * yc[i, j]

    return xp, yp, zp

def mapc2p_brick(xc, yc):
    import os
    """
    Maps (xc, yc) coordinates to brick coordinates

    Parameters:
    xc : numpy array
        X-coordinates in the range [0,1].
    yc : numpy array
        Y-coordinates in the range [0,1].

    Returns:
    xp : numpy array
        Mapped X-coordinates.
    yp : numpy array
        Mapped Y-coordinates.
    zp : numpy array
        Z-coordinates (zeros).
    """
    xc = 1  * xc 
    yc = 1 * yc 

    # Path to brick.dat file
    file_dir = os.path.dirname(__file__)
    brick_dat_path = os.path.join(file_dir, 'brick.dat')

    # Load brick data
    brick_data = np.loadtxt(brick_dat_path )
    mi, mj = int(brick_data[0, 0]), int(brick_data[0, 1])
    xv, yv = brick_data[1:, 0], brick_data[1:, 1]
    
    xp = (xv[blocknumber] + xc) / mi
    yp = (yv[blocknumber] + yc) / mj
    zp = np.zeros_like(xp)

    return xp, yp, zp

def mapc2p_cart(xc, yc):
    xp = 2 * xc - 1
    yp = 2 * yc - 1
    zp = np.zeros_like(xp)  
    return xp, yp, zp

def bilinear_help(alpha, xi, eta):
    xpc = np.array([-alpha, -1, 1, alpha])
    ypc = np.array([alpha, 1, 1, alpha])

    a = np.array([xpc[0], ypc[0]])
    u1 = np.array([xpc[3] - xpc[0], ypc[3] - ypc[0]])
    v1 = np.array([xpc[1] - xpc[0], ypc[1] - ypc[0]])
    v2 = np.array([xpc[2] - xpc[3], ypc[2] - ypc[3]])

    xb=np.zeros_like(xi)
    yb=np.zeros_like(eta)

    xb = a[0] + u1[0] * xi + v1[0] * eta + (v2[0] - v1[0]) * xi * eta
    yb = a[1] + u1[1] * xi + v1[1] * eta + (v2[1] - v1[1]) * xi * eta

    return xb, yb

def mapc2p_fivepatch(xc, yc, alpha):
    if isinstance(xc, (float, int)):  # Checking  if xc is scalar
        # Handle scalar input appropriately
        # For instance, you might just calculate for single values
        m = 1
        n = 1
    else:
        # Handling it as an array
        m, n = xc.shape
    
    if isinstance(xc, (float, int)):
        xc = np.array([xc])
        yc = np.array([yc])


    if blocknumber == 2:
        xp = (2 * xc - 1) * alpha
        yp = (2 * yc - 1) * alpha
    else:
        if blocknumber == 0:
            xc1 = xc
            yc1 = 1 - yc
            xp, yp = bilinear_help(alpha, xc1.ravel(), yc1.ravel())
            yp = -yp
        elif blocknumber == 1:
            xc1 = yc
            yc1 = 1 - xc
            yp, xp = bilinear_help(alpha, xc1.ravel(), yc1.ravel())
            xp = -xp
        elif blocknumber == 3:
            xc1 = yc
            yc1 = xc
            yp, xp = bilinear_help(alpha, xc1.ravel(), yc1.ravel())
        elif blocknumber == 4:
            xc1 = xc
            yc1 = yc
            xp, yp = bilinear_help(alpha, xc1.ravel(), yc1.ravel())
        else:
            raise ValueError(f"blockno = {blocknumber} is not valid.")

    xp = xp.reshape(m, n)
    yp = yp.reshape(m, n)
    zp = np.zeros_like(xp)
    
    return xp, yp, zp

def mapc2p_disk_sp(xc, yc):
    # Disk mapping used for the sphere
    d = np.maximum(np.abs(xc), np.abs(yc))
    d = np.maximum(d, 1e-10)  
    D = np.sin((np.pi * d) / 2) / np.sqrt(2)  
    R = np.ones_like(d)  
    center = D - np.sqrt(R**2 - D**2)

    xp = (D / d) * np.abs(xc)
    yp = (D / d) * np.abs(yc)

    ij = np.where(np.abs(yc) >= np.abs(xc))
    yp[ij] = center[ij] + np.sqrt(R[ij]**2 - xp[ij]**2)

    ij = np.where(np.abs(xc) >= np.abs(yc))
    xp[ij] = center[ij] + np.sqrt(R[ij]**2 - yp[ij]**2)

    xp*=np.sign(xc)
    yp *= np.sign(yc)

    return xp, yp

def rotate_map(xp, yp, zp):
    # Load rotation matrix from 'rrot.dat'
    R = np.loadtxt('rrot.dat')
    m,n=xp.shape
    
    if m > n:  
        z = np.column_stack((xp, yp, zp))
        Rz = R @ z.T
        xp = Rz[0, :].T
        yp = Rz[1, :].T
        zp = Rz[2, :].T
    else:
        Rz = R @ z.T
        xp = Rz[0, :]
        yp = Rz[1, :]
        zp = Rz[2, :]

    return xp, yp, zp


def mapc2p_pillowsphere(xc1, yc1):
    global comp_grid
    comp_grid = False 
    xc, yc, _ = mapc2p_cart(xc1, yc1)
    r1=1
    xp = xc
    yp = yc
    
    if blocknumber == 0:
        zp = np.zeros_like(xp)+1
    else:
        zp = -np.zeros_like(xp)-1

    if comp_grid:
        return xp, yp, zp

    
    d = np.maximum(xc - 1, 0) + np.maximum(-1 - xc, 0)
    xc = (1 - d) / (1 + d) * xc

    d = np.maximum(yc - 1, 0) + np.maximum(-1 - yc, 0)
    yc = (1 - d) / (1 + d) * yc

    
    xp, yp = mapc2p_disk_sp(xc, yc)

    r2 = np.minimum(xp**2 + yp**2, 1)
    zp = np.sqrt(1 - r2)

    
    mghost = (np.abs(xc) > 1) | (np.abs(yc) > 1)
    zp[mghost] = -zp[mghost]

    if blocknumber == 1:
        zp = -zp

    return xp, yp, zp


def mapc2p(xc, yc):
    global notpillowsphere  
    map_type = 'pillow'
    alpha = 0.4
    
    if map_type == 'pillow':
        notpillowsphere = False
        xp, yp, zp = mapc2p_pillowsphere(xc, yc)
    
    elif map_type == 'pillowsphere5':
        notpillowsphere = True
        xc1, yc1, zc1 = mapc2p_fivepatch(0.5, 0.5, alpha)
        xc1 = (xc1 + 1) / 2
        yc1 = (yc1 + 1) / 2
        xp, yp, zp = mapc2p_pillowsphere(xc1, yc1)
        v = [xp, yp, zp]
        
        xp, yp, zp = mapc2p_fivepatch(xc, yc, alpha)
        xc = (xp + 1) / 2
        yc = (yp + 1) / 2
        xp, yp, zp = mapc2p_pillowsphere(xc, yc)
        s = 0.0
        xp = xp + s * v[0]
        yp = yp + s * v[1]
        zp = zp + s * v[2]
    
    return xp, yp



#--------------------------
def setplot(plotdata):
#--------------------------
    
    """ 
    Specify what is to be plotted at each frame.
    Input:  plotdata, an instance of ClawPlotData.
    Output: a modified version of plotdata.
    
    """ 


    from clawpack.visclaw import colormaps
    import clawpack.forestclaw as pyclaw

    plotdata.clearfigures()  # clear any old figures,axes,items data
    plotdata.format = 'forestclaw'
    
    # ------------------------------------------------------------
    # Figure for pcolor plot
    # ------------------------------------------------------------

    plotfigure = plotdata.new_plotfigure(name='q[0]', figno=0)

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.xlimits = 'auto'
    plotaxes.ylimits = 'auto'
    plotaxes.title = 'q[0]'
    plotaxes.scaled = True

    # Set up for item on these axes:
    plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
    plotitem.plot_var = set_blocknumber
    plotitem.pcolor_cmap = colormaps.yellow_red_blue
    plotitem.MappedGrid = True
    plotitem.mapc2p = mapc2p
    plotitem.pcolor_cmin = 0.0
    plotitem.pcolor_cmax = 1.0
    plotitem.add_colorbar = True
    plotitem.amr_celledges_show = [False]
    plotitem.amr_patchedges_show = [True, True,True,False,False]
    plotitem.show = True       # show on plot?
    
   
    plotfigure = plotdata.new_plotfigure(name='filament (tikz)', figno=1)
    plotfigure.use_for_kml = True
    plotfigure.kml_xlimits = [0,2]
    plotfigure.kml_ylimits = [0,2]

    mx = 8
    maxlevel = 4
    resolution = mx*2**maxlevel
    figsize = [4.0,4.0]
    dpi = resolution/figsize[0]

    plotfigure.kml_figsize = figsize  
    plotfigure.kml_dpi = dpi

    # Color axis : transparency below 0.1*(cmax-cmin)
    cmin = 0
    cmax = 1
    cmap = colormaps.yellow_red_blue  # transparent --> light blue --> dark blue

    # Water
    plotaxes = plotfigure.new_plotaxes('tikz')
    plotaxes.xlimits = [0,2]
    plotaxes.ylimits = [0,2]
    plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
    plotitem.plot_var = set_blocknumber   # Plot height field h.    
    plotitem.MappedGrid = True
    plotitem.mapc2p = mapc2p
    plotitem.pcolor_cmap = cmap
    plotitem.pcolor_cmin = cmin
    plotitem.pcolor_cmax = cmax

    def kml_colorbar(filename):
        geoplot.kml_build_colorbar(filename,cmap,cmin,cmax)

    plotfigure.kml_colorbar = kml_colorbar


    #-----------------------------------------
    # Figures for gauges
    #-----------------------------------------
    plotfigure = plotdata.new_plotfigure(name='q', figno=300, \
                    type='each_gauge')
    plotfigure.clf_each_gauge = True

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.xlimits = 'auto'
    plotaxes.ylimits = 'auto'
    plotaxes.title = 'q'

    # Plot q as blue curve:
    plotitem = plotaxes.new_plotitem(plot_type='1d_plot')
    plotitem.plot_var = 0
    plotitem.plotstyle = 'b-'

    #-----------------------------------------

    # Parameters used only when creating html and/or latex hardcopy
    # e.g., via clawpack.visclaw.frametools.printframes:

    plotdata.printfigs = True                # print figures
    plotdata.print_format = 'png'            # file format
    plotdata.print_framenos = 'all'          # list of frames to print
    plotdata.print_fignos = [0,1]            # list of figures to print
    plotdata.html = True                    # create html files of plots?
    plotdata.html_homelink = '../README.html'   # pointer for top of index
    plotdata.html_movie = 'JSAnimation'      # new style, or "4.x" for old style
    plotdata.latex = False                    # create latex file of plots?
    plotdata.latex_figsperline = 2           # layout of plots
    plotdata.latex_framesperline = 1         # layout of plots
    plotdata.latex_makepdf = False           # also run pdflatex?

    plotdata.kml = False      # Set to true to get tikz output

    return plotdata

if __name__=="__main__":
    from clawpack.visclaw.plotclaw import plotclaw
    plotclaw(outdir='.',setplot=setplot,plotdir='_plots',format='forestclaw')



    
