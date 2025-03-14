const Delay = (ms) => new Promise(res => setTimeout(res, ms));

let visible = false;

function toggleVisible(force) {
    visible = !visible;

    if (typeof force == 'boolean') {
        visible = force;
    }

    SetNuiFocus(visible, visible);

    SendNuiMessage(JSON.stringify({
        visible
    }))
}

RegisterCommand('vehicle', toggleVisible)
RegisterKeyMapping('vehicle', 'spawner de veiculos', 'keyboard', 'OEM_6');
RegisterKeyMapping('__cfx_nui:close', 'Close da NUI de veiculos', 'keyboard', 'ESCAPE');
RegisterNuiCallbackType('spawnClick');
on('__cfx_nui:spawnClick', async (data) => {
    toggleVisible(false)

    const hash = GetHashKey(data.hash);
    const playerPed = PlayerPedId();

    RequestModel(hash);

    while (!HasModelLoaded(hash)) {
        await Delay(10)
    }

    const [playerX, playerY, playerZ] = GetEntityCoords(playerPed);
    const vehicle = await CreateVehicle(hash, playerX, playerY, playerZ, 0, true, false);

    SetModelAsNoLongerNeeded(hash);
    
    SetPedIntoVehicle(playerPed, vehicle, -1)
})

RegisterNuiCallbackType('close');
on('__cfx_nui:close', () => {
    toggleVisible(false)
})