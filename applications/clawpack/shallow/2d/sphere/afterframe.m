setviews;

parms = read_vars();

fprintf('%10s : %12.4e\n','qmin',qmin);
fprintf('%10s : %12.4e\n','qmax',qmax);


if (PlotType  == 4)
    % Do something
    [amr1d,t1d] = readamrdata(1,Frame,'./1d_latitude/_output','ascii','',false);
    if abs(t1d-t) > 1e-8
        error('afterframe : 1d and 2d times do not agree.')
    end
    % (-90,180) and (90,0) --> 180/(-180)*(x - 90) + 0 = 90-x
    amr1d.xlow =  0;  % (90-amr1d.xlow)*pi/180;  
    amr1d.dx = amr1d.dx*pi/180;   
    fprintf('%10s : %12.4e\n','qmin(1d)',min(amr1d.data(1,:)));
    fprintf('%10s : %12.4e\n','qmax(1d)',max(amr1d.data(1,:)));

    [q1d,xc1d,h1d]  = plotframe1ez(amr1d,1,'b-','sphere_1d','');
    set(h1d,'linewidth',2)

    qmin = min([qmin,min(q1d)]);
    qmax = max([qmax,max(q1d)]);

    xlabel('Latitude','fontsize',16)
    ylabel('h(phi,t)','fontsize',16)

    axis([0,pi,qmin,qmax])
    set(gca,'fontsize',16)

    ylim([-0.1,2])
    h = getlegendinfo();
    legend(h);
else

    if (PlotParallelPartitions == 0)
        d = parms.hin - parms.hout;
        clim([parms.hout-d/10, parms.hin+d/10]);
    end
    colorbar;
    
    lv = linspace(0.5,1.5,30);
    drawcontourlines(lv)
    showpatchborders(1:10);
    setpatchborderprops('linewidth',1)
    
    daspect([1,1,1]);
    s = 0.2;
    axis([-1-s,1+s,-1-s,1+s,-1-s,1+s])
    view([32,24])
    set(gca,'clipping','off')
end

NoQuery = 0;
prt = false;
MaxFrames = 81;
if (prt)
  filename = framename(Frame,'sphere0000','png');
  print('-dpng',filename);
end

shg