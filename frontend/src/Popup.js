import React, {useState} from "react"
import "./styles/popup.css"

function EquipmentPopup({onClose, onSubmit}){ 
    const [equipmentName, setEquipmentName] = useState("")
    const [equipmentYear, setEquipmentYear] = useState("")
    const [equipmentClass, setEquipmentClass] = useState("")
    const [equipmentImages, setEquipmentImages] = useState("")
    const [equipmentReports, setEquipmentReports] = useState("")

    const Submit = () => {
        if (!equipmentName || !equipmentYear || equipmentClass){
            //add message to input all fields
        }
        onSubmit(equipmentName, equipmentYear, equipmentClass, equipmentImages, equipmentReports)
        setEquipmentName("")
        setEquipmentYear("")
        setEquipmentClass("")
        setEquipmentImages("")
        setEquipmentReports("")
        onClose()
    }
    return (
    <div className="popup-overlay">
        <div className="popup">
        <h2>Add Equipment</h2>

        <label>Equipment Name:</label>
        <input
            type="text"
            value={equipmentName}
            onChange={(e) => setEquipmentName(e.target.value)}
            placeholder="e.g. John Deer Tractor"
        />

        <label>Equipment Class</label>
        <input
            type="text"
            value={equipmentClass}
            onChange={(e) => setEquipmentClass(e.target.value)}
            placeholder="e.g. Vehicle"
        />


        <label>Equipment Year:</label>
        <input
            type="text"
            value={equipmentYear}
            onChange={(e) => setEquipmentYear(e.target.value)}
            placeholder="e.g. 2020"
        />

        <label>Equipment Images:</label>
        <input
            type="file"
            onChange={(e) => setEquipmentImages(e.target.value)}
            />
        
        <label>Equipment Reports:</label>
        <input
            type="file"
            onChange={(e) => setEquipmentReports(e.target.value)}
            />

        <div className="popup-buttons">
            <button onClick={Submit}>Add</button>
            <button onClick={onClose}>Cancel</button>
        </div>
        </div>
    </div>
    );
};

export default EquipmentPopup