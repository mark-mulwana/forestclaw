
""" 
Plot swirl using Clawpack's visclaw graphics.  This file can be run as ; 

    % python plot_swirl.py

To learn more about visclaw graphics, see www.clawpack.org
    
""" 

from clawpack.visclaw import colormaps
import clawpack.forestclaw as pyclaw 
import matplotlib.pyplot as plt
import numpy as np
import os

#Path to setprob.data file
file_path = os.path.dirname(__file__)
setprob_data_path = os.path.join(file_path, 'setprob.data')


# Read the file and extract values
with open(setprob_data_path, 'r') as file:
    lines = file.readlines()
    example = int(lines[0].split()[0])    
    alpha = float(lines[1].split()[0])    
    beta = float(lines[2].split()[0]) 
    revs_per_second = float(lines[3].split()[0]) 

def set_blocknumber(current_data):
    global blocknumber
    blocknumber = current_data.patch.block_number
    return current_data.q[0,:,:]

def mapc2p_brick(xc, yc):
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

def mapc2p_torus(xc, yc, alpha, beta):
    
    pi2=2*np.pi

    r=alpha*(1+beta*np.sin(pi2*xc))
    R=1+r*np.cos(pi2*yc)

    xp=R*np.cos(pi2*xc)
    yp=R*np.sin(pi2*xc)
    zp=r*np.sin(pi2*yc)
    return xp, yp, zp

def mapc2p(xc, yc):
    xc1,yc1,_=mapc2p_brick(xc,yc)
    xp,yp,zp=mapc2p_torus(xc1,yc1,alpha,beta)
    
    return xp, yp



#--------------------------
def setplot(plotdata):
#--------------------------
    
    """ 
    Specify what is to be plotted at each frame.
    Input:  plotdata, an instance of ClawPlotData.
    Output: a modified version of plotdata.
    
    """ 

    plotdata.clearfigures()  # clear any old figures,axes,items data
    
    # ------------------------------------------------------------
    # Figure for pcolor plot
    # ------------------------------------------------------------

    plotfigure = plotdata.new_plotfigure(name='q[0]', figno=0)

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.xlimits = 'auto'
    plotaxes.ylimits = 'auto'
    plotaxes.title = 'q[0]'
    plotaxes.scaled = False
    

    # Set up for item on these axes:
    plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
    plotitem.plot_var = set_blocknumber 
    plotitem.pcolor_cmap = colormaps.yellow_red_blue
    
    

    plotitem.MappedGrid = True
    plotitem.mapc2p = mapc2p
    plotitem.pcolor_cmin = 0.0
    plotitem.pcolor_cmax = 1.0
    

    plotitem.add_colorbar = True
    plotitem.amr_celledges_show=[False, False, False, False]
    plotitem.amr_patchedges_show =[True, True, False,False]
    plotitem.show = True       # show on plot?

    
    # ------------------------------------------------------------
    # Figure for contour plot
    # ------------------------------------------------------------
    plotfigure = plotdata.new_plotfigure(name='contour', figno=1)

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.xlimits = 'auto'
    plotaxes.ylimits = 'auto'
    plotaxes.title = 'q[0]'
    plotaxes.scaled =False

    # Set up for item on these axes:
    plotitem = plotaxes.new_plotitem(plot_type='2d_contour')
    plotitem.plot_var = set_blocknumber 
    plotitem.contour_nlevels = np.linspace(0.0,1.0,10)
    plotitem.MappedGrid = True
    plotitem.mapc2p = mapc2p
    plotitem.amr_contour_colors = ['k','k','k']
    plotitem.show = True       # show on plot?

   
    # Parameters used only when creating html and/or latex hardcopy
    # e.g., via clawpack.visclaw.frametools.printframes:

    plotdata.printfigs = True                # print figures
    plotdata.print_format = 'png'            # file format
    plotdata.print_framenos = 'all'          # list of frames to print
    plotdata.print_fignos = [0]            # list of figures to print
    plotdata.html = True                    # create html files of plots?
    plotdata.html_homelink = '../README.html'   # pointer for top of index
    plotdata.html_movie = 'JSAnimation'      # new style, or "4.x" for old style
    plotdata.latex = False                    # create latex file of plots?
    plotdata.latex_figsperline = 2           # layout of plots
    plotdata.latex_framesperline = 1         # layout of plots
    plotdata.latex_makepdf = False           # also run pdflatex?
    plotdata.format = 'forestclaw'

    plotdata.kml = False      # Set to true to get tikz output

    return plotdata



if __name__=="__main__":
    from clawpack.visclaw.plotclaw import plotclaw
    plotclaw(outdir='.',setplot=setplot,plotdir='_plots',format='forestclaw')



    
