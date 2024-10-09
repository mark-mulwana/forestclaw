
""" 
Plot swirl using Clawpack's visclaw graphics.  This file can be run as ; 

    % python plot_swirl.py

To learn more about visclaw graphics, see www.clawpack.org
    
""" 


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
    plotitem = plotaxes.new_plotitem(plot_type='2d_imshow')
    plotitem.plot_var = 0
    plotitem.imshow_cmap = colormaps.yellow_red_blue
    plotitem.imshow_cmin = 0.0
    plotitem.imshow_cmax = 1.0
    plotitem.add_colorbar = True
    plotitem.amr_celledges_show = [False, False, False, False,False,False,False,False]
    plotitem.amr_patchedges_show = [True, True,True,True,True,True,False,False]
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
    plotaxes.scaled = True

    # Set up for item on these axes:
    plotitem = plotaxes.new_plotitem(plot_type='2d_contour')
    plotitem.plot_var = 0
    plotitem.contour_nlevels = 20
    plotitem.contour_min = 0.01
    plotitem.contour_max = 0.99
    plotitem.amr_contour_colors = ['k','k','k']
    plotitem.show = True       # show on plot?

    #-----------------------------------------

    # Parameters used only when creating html and/or latex hardcopy
    # e.g., via clawpack.visclaw.frametools.printframes:

    plotdata.printfigs = True                # print figures
    plotdata.print_format = 'png'            # file format
    plotdata.print_framenos = "all"          # list of frames to print
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

def plot_layout(current_data):
    import matplotlib.pyplot as plt
    from clawpack.visclaw import colormaps
    
    
    #Accessing both current figure and axes (plot area)
    fig = plt.gcf()
    axes = plt.gca()

    # Get the last plotted image (imshow)
    imshow = axes.images[-1]  

    # Set the colormap to yellow_red_blue for the plot
    imshow.set_cmap(colormaps.yellow_red_blue)
    
    # Add horizontal colorbar to the plot
    #cbar = fig.colorbar(imshow, ax=axes, orientation='horizontal')
    
    # Set the color limits to match the colormap
    min_v=0.0
    max_v=1.0
    imshow.set_clim(min_v, max_v)  

    # Adjust the colorbar's position and appearance
    #cbar.ax.set_position([0.3, 0.001, 0.3, 0.01])  
    #fig.tight_layout(pad=0.3)
    #plt.set_cmap('viridis')

    # Grid lines disabled
    plt.grid(False)

if __name__=="__main__":
    from clawpack.visclaw.plotclaw import plotclaw
    plotclaw(outdir='.',setplot=setplot,plotdir='_plots',format='forestclaw')



    
