"""Method to translate a Dragonfly Model to a VisualizationSet."""
import math

from ladybug_geometry.geometry3d import Vector3D, Point3D, Face3D
from ladybug.color import Color
from ladybug_display.geometry3d import DisplayLineSegment3D, DisplayMesh3D
from ladybug_display.visualization import ContextGeometry
from honeybee.boundarycondition import boundary_conditions as bcs
from honeybee.face import Face
from dragonfly.windowparameter import DetailedWindows
from dragonfly.context import ContextShade

from honeybee_display.attr import RoomAttribute
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

        -   Slabs_On_Grade_to_Walls -- A ContextGeometry for the envelope edges
            where ground floor slabs meet exterior walls (or roofs).

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


def model_opening_projection_to_vis_set(
    base_df_model, openings_hb_model, wall_modifier_data=None,
    projection_distance=0, angle_tolerance=None, exclude_existing_openings=True,
    unmatched_color=None, overwritten_color=None, reset_coordinates=False
):
    """Translate s Dragonfly Model to a VisualizationSet that highlights projected openings.

    Args:
        base_df_model: A Dragonfly Model object for the base model to which orphaned
            honeybee Apertures and Doors will be projected onto the Room2Ds.
        openings_hb_model: A Honeybee Model object for the model containing orphaned
            honeybee Apertures and Doors to be projected onto the Room2Ds of the
            base_df_model.
        wall_modifier_data: An optional array of wall modifier lines and/pr polygons
            that customize the properties of walls across the model. When supplied,
            these will be used to highlight any openings that were successfully
            assigned to the Room2D but are overwritten by a wall modifiers,
            essentially removing openings in order to assign a special boundary
            condition or air boundary property. (Default: None).
        projection_distance: An optional number to be used to project the
            Aperture/Door geometry onto Room2D wall segments. If specified,
            then openings within this distance of the parent wall will be
            projected and added. Otherwise, if it is zero, Apertures/Doors
            will only be added if they are coplanar with the Room2D wall
            segment within the base_df_model tolerance.
        angle_tolerance: The max angle difference in degrees that wall segments
            and sub-faces can differ from one another in order for the sub-face
            to be projected onto the geometry. If None, the angle tolerance
            of the base_df_model will be used. (Default: None).
        exclude_existing_openings: A boolean to note whether the existing openings
            assigned to the Room2Ds of the base_df_model should be excluded in
            the resulting visualization (so the visualization only highlights
            the newly-added openings) or they should be included alongside
            the newly-added openings. (Default: True).
        unmatched_color: An optional ladybug Color to set the color of the openings
            that were not successfully added to any Room2Ds in the base_df_model.
            If None, a default red color will be used. (Default: None).
        overwritten_color: An optional ladybug Color to set the color of the openings
            that were successfully added to the Room2Ds but overwritten by the
            wall_modifier_data. If None, a default bright green color will be
            used. (Default: None).
        reset_coordinates: Boolean to note whether the coordinate system of the
            model should be reset in the resulting visualization set such that
            the model sits at the origin. This is useful when the resulting
            visualization platform is meant to orbit around the world
            origin. (Default: False).
    """
    # ensure the model units and coordinate system are synced
    if not openings_hb_model.units == base_df_model.units:
        openings_hb_model.convert_to_units(base_df_model.units)
    if base_df_model.reference_vector is not None:
        openings_hb_model.move(base_df_model.reference_vector)

    # add the openings of the HB model to the base DF one and track the unmatched ones
    tol = base_df_model.tolerance
    ang_tol = base_df_model.angle_tolerance if angle_tolerance is None else angle_tolerance
    win_geo = openings_hb_model.apertures + openings_hb_model.doors
    unassigned_dict = {geo.identifier: geo for geo in win_geo}
    for room in base_df_model.room_2ds:
        assigned_geo = room.assign_sub_faces(
            win_geo, projection_distance,
            overwrite=exclude_existing_openings,
            tolerance=tol, angle_tolerance=ang_tol
        )
        if assigned_geo is not None:
            for a_geo in assigned_geo:
                unassigned_dict.pop(a_geo.identifier, None)

    # collect shades assigned to the sub-faces so they can be displayed
    for shd_grp in openings_hb_model.grouped_shades:
        base_obj = shd_grp[0]
        shd_geo = [s.geometry for s in shd_grp]
        con_shade = ContextShade(base_obj.identifier, shd_geo, base_obj.is_detached)
        base_df_model.add_context_shade(con_shade)

    # if wall modifiers were supplied, apply them and track the overwritten window pars
    overwritten_sub_faces = []
    if wall_modifier_data is not None and len(wall_modifier_data) != 0:
        wall_modifiers = base_df_model.deserialize_wall_modifiers(wall_modifier_data)
        original_model = base_df_model.duplicate()
        for story in base_df_model.stories:
            try:
                line_geometries, properties = wall_modifiers[story.identifier]
            except KeyError:
                continue  # no modifiers present for this story
            story.modify_wall_properties(line_geometries, properties, tol)
        for orig_room, final_room in zip(original_model.room_2ds, base_df_model.room_2ds):
            zip_obj = zip(
                orig_room.window_parameters,
                final_room.window_parameters,
                final_room.floor_segments
            )
            for o_wp, f_wp, seg in zip_obj:
                if f_wp is None and o_wp is not None:
                    if isinstance(o_wp, DetailedWindows):
                        ext_vec = Vector3D(0, 0, orig_room.floor_to_ceiling_height)
                        wall_f = Face('dummy', Face3D.from_extrusion(seg, ext_vec))
                        wall_f.boundary_condition = bcs.outdoors
                        o_wp.add_window_to_face(wall_f, tol)
                        overwritten_sub_faces.extend(wall_f.sub_faces)

    # reset the coordinate system for the final visualization if requested
    if reset_coordinates:
        min_pt, max_pt = base_df_model.min, base_df_model.max
        z_val = base_df_model.average_height - base_df_model.average_height_above_ground
        center = Point3D((max_pt.x + min_pt.x) / 2, (max_pt.y + min_pt.y) / 2, z_val)
        base_df_model.reset_coordinate_system(center)
        # move the geometry using a vector that is the inverse of the origin
        ref_vec = Vector3D(-center.x, -center.y, -center.z)
        for geo in unassigned_dict.values():
            geo.move(ref_vec)
        for geo in overwritten_sub_faces:
            geo.move(ref_vec)

    # create the Honeybee Model from the Dragonfly ones
    hb_model = base_df_model.to_honeybee(
        'District', exclude_plenums=False, solve_ceiling_adjacencies=False,
        enforce_adj=False, enforce_solid=True
    )[0]

    # convert the Honeybee Model to a VisualizationSet
    room_attrs = [RoomAttribute('Room Names', ['display_name'], False, True)]
    vis_set = hb_model_to_vis_set(hb_model, color_by='None', room_attrs=room_attrs)

    # collect the colored opening geometry to be added to the visualization set
    ap_color = Color(64, 180, 255, 100)
    dr_color = Color(160, 150, 100)
    unmatched_color = Color(225, 0, 0) if unmatched_color is None else unmatched_color
    overwritten_color = Color(0, 225, 0) if overwritten_color is None else overwritten_color
    ap_geo = [
        DisplayMesh3D(f.geometry.triangulated_mesh3d, color=ap_color)
        for f in hb_model.apertures
    ]
    dr_geo = [
        DisplayMesh3D(f.geometry.triangulated_mesh3d, color=dr_color)
        for f in hb_model.doors
    ]
    unmatched_geo = [
        DisplayMesh3D(f.geometry.triangulated_mesh3d, color=unmatched_color)
        for f in unassigned_dict.values()
    ]
    overwritten_geo = [
        DisplayMesh3D(f.geometry.triangulated_mesh3d, color=overwritten_color)
        for f in overwritten_sub_faces
    ]

    # add the opening geometry to the visualization set as ContextGeometry
    if len(ap_geo) != 0:
        vis_set.add_geometry(ContextGeometry('Aperture', ap_geo))
    if len(dr_geo) != 0:
        vis_set.add_geometry(ContextGeometry('Door', dr_geo))
    if len(unmatched_geo) != 0:
        vis_set.add_geometry(ContextGeometry('Unmatched', unmatched_geo))
    if len(overwritten_geo) != 0:
        name = 'Overwritten by Boundary Conditions'
        con_geo = ContextGeometry(name.replace(' ', '_'), overwritten_geo)
        con_geo.display_name = name
        vis_set.add_geometry(con_geo)
    return vis_set
