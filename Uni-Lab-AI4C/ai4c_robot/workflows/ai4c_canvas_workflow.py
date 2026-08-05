from typing import Annotated

from pydantic import Field
from unilabos.workflow.authoring import device, workflow, workflow_output

from ai4c_robot.devices.ai4c_robot_arm.device import AI4CRobotArmDevice

AI4C_robot_arm: AI4CRobotArmDevice = device(
    "71ae70d1-397c-5d80-ac32-350cade86993"
)


@workflow(
    workflow_uuid="315a8273-e38c-5add-a655-bb7228fe077f",
    displayname="AI4C 孔板搬运联调",
    description="从上料架依次经过移液、磁搅和 HPLC 工位后放入下料架。",
)
def szlab_canvas_workflow(
    *,
    loading_position: Annotated[
        int,
        Field(title="上料架位置", description="范围 1-8。", ge=1, le=8),
    ] = 1,
    unloading_position: Annotated[
        int,
        Field(title="下料架位置", description="范围 1-8。", ge=1, le=8),
    ] = 1,
):
    # unilab:node_uuid=8cdd08c1-0943-529c-9007-c9f58ed98641
    picked_from_loading_rack = AI4C_robot_arm.pick_well_plate_from_loading_rack(  # noqa: F841
        position=loading_position
    )
    # unilab:node_uuid=e81c6dbd-4523-51a1-8a5a-ac17df749b26
    placed_at_pipetting = AI4C_robot_arm.place_well_plate_to_pipetting_station()  # noqa: F841
    # unilab:node_uuid=a28b9580-cea2-5d70-9795-fcd71e224e3f
    picked_from_pipetting = AI4C_robot_arm.pick_well_plate_from_pipetting_station()  # noqa: F841
    # unilab:node_uuid=968fe392-47a9-5312-9d9a-384ba9c3d96a
    placed_at_magnetic_stirrer = (  # noqa: F841
        AI4C_robot_arm.place_well_plate_to_magnetic_stirrer()
    )
    # unilab:node_uuid=ad807f64-60f6-5245-a2e7-88e0987e11db
    picked_from_magnetic_stirrer = (  # noqa: F841
        AI4C_robot_arm.pick_well_plate_from_magnetic_stirrer()
    )
    # unilab:node_uuid=c4fb2499-ad3b-5edf-9c74-891b95a10df9
    placed_at_hplc = AI4C_robot_arm.place_well_plate_to_hplc_station()  # noqa: F841
    # unilab:node_uuid=459eabb0-847a-53eb-8edf-f6e73ba85edc
    picked_from_hplc = AI4C_robot_arm.pick_well_plate_from_hplc_station()  # noqa: F841
    # unilab:node_uuid=296ef27a-a9cf-5e56-8ca5-23e2c2fb8a91
    placed_at_unloading_rack = AI4C_robot_arm.place_well_plate_to_unloading_rack(  # noqa: F841
        position=unloading_position
    )
    return workflow_output()
