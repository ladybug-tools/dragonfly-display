"""Method to translate a Dragonfly Model to a VisualizationSet."""
import math

from ladybug_geometry.geometry3d import Vector3D, Point3D
from ladybug.color import Color
from ladybug_display.geometry3d import DisplayLineSegment3D
from ladybug_display.visualization import ContextGeometry

from honeybee_display.model import model_to_vis_set as hb_model_to_vis_set
from honeybee_display.model import model_comparison_to_vis_set as \
    hb_model_comparison_to_vis_set
from honeybee_display.model import model_envelope_edges_to_vis_set as \
    hb_model_envelope_edges_to_vis_set


def model_to_vis_set(
    model, use_multiplier=True, exclude_plenums=False,
    solve_ceiling_adjacencies=False, merge_method='None',
    color_by='type', include_wireframe=True, use_mesh=True,
    hide_color_by=False, room_attrs=None, face_attrs=None,
    grid_display_mode='Default', hide_grid=False, reset_coordinates=False
):
    """Translate a Dragonfly Model to a VisualizationSet.

    Args:
        model: A Dragonfly Model object to be converted to a VisualizationSet.
        use_multiplier: If True, the multipliers on this Model's Stories will be
            passed along to the generated Honeybee Room objects, indicating the
            simulation will be run once for each unique room and then results
            will be multiplied. If False, full geometry objects will be written
            for each and every floor in the building that are represented through
            multipliers and all resulting multipliers will be 1. (Default: True).
        exclude_plenums: Boolean to indicate whether ceiling/floor plenum depths
            assigned to Room2Ds should be ignored during translation. This
            results in each Room2D translating to a single Honeybee Room at
            the full floor_to_ceiling_height instead of a base Room with (a)
            plenum Room(s). (Default: False).
        solve_ceiling_adjacencies: Boolean to note whether adjacencies should be
            solved between interior stories when Room2D floor and ceiling
            geometries are coplanar. This ensures that Surface boundary
            conditions are used instead of Adiabatic ones. Note that this input
            has no effect when the object_per_model is Story. (Default: False).
        merge_method: An optional text string to describe how the Room2Ds should
            be merged into individual Rooms during the translation. Specifying a
            value here can be an effective way to reduce the number of Room volumes
            in the resulting Model. Note that Room2Ds will only be merged if they
            form a contiguous volume. Otherwise, there will be multiple Rooms per
            zone or story, each with an integer added at the end of their
            identifiers. Choose from the following options:

            * None - No merging of Room2Ds will occur
            * Zones - Room2Ds in the same zone will be merged
            * PlenumZones - Only plenums in the same zone will be merged
            * Stories - Rooms in the same story will be merged
            * PlenumStories - Only plenums in the same story will be merged

        color_by: Text that dictates the colors of the Model geometry.
            If none, only a wireframe of the Model will be generated, assuming
            include_wireframe is True. This is useful when the primary purpose of
            the visualization is to display results in relation to the Model
            geometry or display some room_attrs or face_attrs as an AnalysisGeometry
            or Text labels. (Default: type). Choose from the following:

            * type
            * boundary_condition
            * None

        include_wireframe: Boolean to note whether a ContextGeometry dedicated to
            the Model Wireframe (in DisplayLineSegment3D) should be included
            in the output VisualizationSet. (Default: True).
        use_mesh: Boolean to note whether the colored model geometries should
            be represented with DisplayMesh3D objects (True) instead of DisplayFace3D
            objects (False). Meshes can usually be rendered faster and they scale
            well for large models but all geometry is triangulated (meaning that
            the wireframe in certain platforms might not appear ideal). (Default: True).
        hide_color_by: Boolean to note whether the color_by geometry should be
            hidden or shown by default. Hiding the color-by geometry is useful
            when the primary purpose of the visualization is to display grid_data
            or room/face attributes but it is still desirable to have the option
            to turn on the geometry.
        room_attrs: An optional list of room attribute objects from the
            honeybee_display.attr module.
        face_attrs: An optional list of face attribute objects from the
            honeybee_display.attr module.
        grid_display_mode: Text that dictates how the ContextGeometry for Model
            SensorGrids should display in the resulting visualization. The Default
            option will draw sensor points. Choose from the following:

            * Default
            * Points
            * Wireframe
            * Surface
            * SurfaceWithEdges
            * None

        hide_grid: Boolean to note whether the SensorGrid ContextGeometry should be
            hidden or shown by default. (Default: False).
        reset_coordinates: Boolean to note whether the coordinate system of the
            model should be reset in the resulting visualization set such that
            the model sits at the origin. This is useful when the resulting
            visualization platform is meant to orbit around the world
            origin. (Default: False).

    Returns:
        A VisualizationSet object that represents the model.
    """
    # reset the coordinate system if requested
    if reset_coordinates:
        model = model.duplicate()
        min_pt, max_pt = model.min, model.max
        z_val = model.average_height - model.average_height_above_ground
        center = Point3D((max_pt.x + min_pt.x) / 2, (max_pt.y + min_pt.y) / 2, z_val)
        model.reset_coordinate_system(center)
    # create the Honeybee Model from the Dragonfly one
    hb_model = model.to_honeybee(
        'District', use_multiplier=use_multiplier, exclude_plenums=exclude_plenums,
        solve_ceiling_adjacencies=solve_ceiling_adjacencies, merge_method=merge_method,
        enforce_adj=False, enforce_solid=True)[0]
    # convert the Honeybee Model to a VisualizationSet
    return hb_model_to_vis_set(
        hb_model, color_by, include_wireframe, use_mesh, hide_color_by,
        room_attrs, face_attrs, grid_display_mode, hide_grid)


def model_envelope_edges_to_vis_set(
    model, coplanar_type='FloorPlatesOnly', mullion_thickness=None,
    reset_coordinates=False
):
    """Translate a Dragonfly Model to a VisualizationSet with edges highlighted.

    Args:
        model: A Dragonfly Model object which will have its edges converted to
            a VisualizationSet.
        coplanar_type: Text to indicate whether any edges between coplanar envelope
            faces should be included in the result. Most coplanar edges in the
            envelope do not correspond to real physical thermal bridges but edges
            where interior floor plates align with exterior walls might result
            in bridges. Choose from the following options. (Default: FloorPlatesOnly).

            * None
            * FloorPlatesOnly
            * All

        mullion_thickness: The maximum difference that apertures or doors can be from
            one another for the edges to be considered a mullion rather than
            a frame. If None, all edges of apertures and doors will be considered
            frames rather than mullions.
        reset_coordinates: Boolean to note whether the coordinate system of the
            model should be reset in the resulting visualization set such that
            the model sits at the origin. This is useful when the resulting
            visualization platform is meant to orbit around the world
            origin. (Default: False).

    Returns:
        A VisualizationSet object that represents the model. This includes these
        objects in the following order, though certain layers may be removed if
        the model contains none of a certain case or if they are not relevant
        given the input options.

        -   Roofs_to_Walls -- A ContextGeometry for the envelope edges where
            roofs meet exterior walls (or exterior floors).

        -   Slabs_to_Walls -- A ContextGeometry for the envelope edges where ground
            floor slabs meet exterior walls (or roofs).

        -   Exposed_Floors_to_Walls -- A ContextGeometry for the envelope edges
            where exposed floors meet exterior walls.

        -   Interior_Floors_to_Walls -- A ContextGeometry for the envelope edges
            where interior floors meet exterior walls.

        -   Walls_to_Walls -- A ContextGeometry for the envelope edges where
            exterior walls meet (as in corners of buildings).

        -   Roof_Ridges -- A ContextGeometry for the envelope edges where exterior
            roofs meet.

        -   Exposed_Floors_to_Floors -- A ContextGeometry for the envelope edges
            where exposed floors meet.

        -   Underground -- A ContextGeometry for the envelope edges where
            underground faces meet.

        -   Window_Frames -- A ContextGeometry for the edges where apertures meet
            their parent exterior wall or roof.

        -   Window_Mullions -- A ContextGeometry for the edges where apertures
            meet one another.

        -   Door_Frames -- A ContextGeometry for the edges where doors meet
            their parent exterior wall or roof.

        -   Door_Mullions -- A ContextGeometry for the edges where doors meet
            one another.
    """
    # reset the coordinate system if requested
    if reset_coordinates:
        model = model.duplicate()
        min_pt, max_pt = model.min, model.max
        z_val = model.average_height - model.average_height_above_ground
        center = Point3D((max_pt.x + min_pt.x) / 2, (max_pt.y + min_pt.y) / 2, z_val)
        model.reset_coordinate_system(center)

    # create the Honeybee Model from the Dragonfly one
    hb_model = model.to_honeybee(
        'District', use_multiplier=False, exclude_plenums=True,
        solve_ceiling_adjacencies=True, enforce_adj=False, enforce_solid=True)[0]

    # make the visualization set of envelope edges
    coplanar_type = str(coplanar_type)
    exclude_coplanar = False if coplanar_type == 'All' else True
    vis_set = hb_model_envelope_edges_to_vis_set(
        hb_model, exclude_coplanar, mullion_thickness)

    # if FloorPlatesOnly option was selected, add it as a layer
    if coplanar_type == 'FloorPlatesOnly':
        color = Color(200, 255, 200)
        up_vec = Vector3D(0, 0, 1)
        min_ang = (math.pi / 2) - math.radians(model.angle_tolerance)
        max_ang = (math.pi / 2) + math.radians(model.angle_tolerance)

        _, _, _, ext_walls_to_walls, _, _, _ = \
            hb_model.classified_envelope_edges(exclude_coplanar=False)
        interior_floor_plate_to_wall = []
        for edge in ext_walls_to_walls:
            if min_ang <= up_vec.angle(edge.v) <= max_ang:
                interior_floor_plate_to_wall.append(edge)
        display_edges = [DisplayLineSegment3D(seg, color, 2)
                         for seg in interior_floor_plate_to_wall]
        edge_id = 'Interior_Floors_to_Walls'
        if len(display_edges) != 0:
            con_geo = ContextGeometry(edge_id, display_edges)
            con_geo.display_name = edge_id.replace('_', ' ')
            insert_index = None
            for i, geo in enumerate(vis_set):
                if geo.identifier in ('Walls_to_Walls', 'Roof_Ridges', 'Roofs_to_Roofs'):
                    insert_index = i
                    break
            vis_set.add_geometry(con_geo, insert_index)

    return vis_set


def model_comparison_to_vis_set(
    base_model, incoming_model, use_multiplier=True, exclude_plenums=False,
    solve_ceiling_adjacencies=False, merge_method='None',
    base_color=None, incoming_color=None, reset_coordinates=False
):
    """Translate two Dragonfly Models to be compared to a VisualizationSet.

    Args:
        base_model: A Dragonfly Model object for the base model used in the
            comparison. Typically, this is the model with more data to be kept.
        incoming_model: A Dragonfly Model object for the incoming model used in the
            comparison. Typically, this is the model with new data to be
            evaluated against the base model.
        use_multiplier: If True, the multipliers on this Model's Stories will be
            passed along to the generated Honeybee Room objects, indicating the
            simulation will be run once for each unique room and then results
            will be multiplied. If False, full geometry objects will be written
            for each and every floor in the building that are represented through
            multipliers and all resulting multipliers will be 1. (Default: True).
        exclude_plenums: Boolean to indicate whether ceiling/floor plenum depths
            assigned to Room2Ds should be ignored during translation. This
            results in each Room2D translating to a single Honeybee Room at
            the full floor_to_ceiling_height instead of a base Room with (a)
            plenum Room(s). (Default: False).
        solve_ceiling_adjacencies: Boolean to note whether adjacencies should be
            solved between interior stories when Room2D floor and ceiling
            geometries are coplanar. This ensures that Surface boundary
            conditions are used instead of Adiabatic ones. Note that this input
            has no effect when the object_per_model is Story. (Default: False).
        merge_method: An optional text string to describe how the Room2Ds should
            be merged into individual Rooms during the translation. Specifying a
            value here can be an effective way to reduce the number of Room volumes
            in the resulting Model. Note that Room2Ds will only be merged if they
            form a contiguous volume. Otherwise, there will be multiple Rooms per
            zone or story, each with an integer added at the end of their
            identifiers. Choose from the following options:

            * None - No merging of Room2Ds will occur
            * Zones - Room2Ds in the same zone will be merged
            * PlenumZones - Only plenums in the same zone will be merged
            * Stories - Rooms in the same story will be merged
            * PlenumStories - Only plenums in the same story will be merged

        base_color: An optional ladybug Color to set the color of the base model.
            If None, a default blue color will be used. (Default: None).
        incoming_color: An optional ladybug Color to set the color of the incoming model.
            If None, a default red color will be used. (Default: None).
            reset_coordinates: Boolean to note whether the coordinate system of the
            model should be reset in the resulting visualization set such that
            the model sits at the origin. This is useful when the resulting
            visualization platform is meant to orbit around the world
            origin. (Default: False).
    """
    # reset the coordinate system if requested
    if reset_coordinates:
        min_pt, max_pt = base_model.min, base_model.max
        z_val = base_model.average_height - base_model.average_height_above_ground
        center = Point3D((max_pt.x + min_pt.x) / 2, (max_pt.y + min_pt.y) / 2, z_val)
        base_model.reset_coordinate_system(center)
        incoming_model.reset_coordinate_system(center)
    # create the Honeybee Models from the Dragonfly ones
    base_model = base_model.to_honeybee(
        'District', use_multiplier=use_multiplier, exclude_plenums=exclude_plenums,
        solve_ceiling_adjacencies=solve_ceiling_adjacencies, merge_method=merge_method,
        enforce_adj=False, enforce_solid=True
    )[0]
    incoming_model = incoming_model.to_honeybee(
        'District', use_multiplier=use_multiplier, exclude_plenums=exclude_plenums,
        solve_ceiling_adjacencies=solve_ceiling_adjacencies, merge_method=merge_method,
        enforce_adj=False, enforce_solid=True
    )[0]
    # convert the Honeybee Model to a VisualizationSet
    return hb_model_comparison_to_vis_set(
        base_model, incoming_model, base_color, incoming_color)
