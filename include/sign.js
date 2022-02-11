CodeBoot.prototype.setupKeys = function (keys) {

    try {
        for (var i=0; i<keys.length; i++) {
            if (typeof keys[i] === 'string') {
                keys[i] = KEYUTIL.getKey(keys[i]);
            }
        }
    } catch (exc) {
        keys = [];
    }

    return keys;
};

CodeBoot.prototype.signString = function (str, key) {

    var algorithm = CodeBoot.prototype.signAlgorithm;

    try {
        var signature = new KJUR.crypto.Signature({ 'alg': algorithm });
        signature.init(key);
        signature.updateString(str);
        return hextob64u(signature.sign());
    } catch (exc) {
        console.log(exc);
        return null;
    }
};

CodeBoot.prototype.verifyString = function (str, sig) {

    var algorithm = CodeBoot.prototype.signAlgorithm;
    var pubkeys = CodeBoot.prototype.setupKeys(CodeBoot.prototype.pubkeys);
    var hexsig = b64utohex(sig);

    for (var i=0; i<pubkeys.length; i++) {

        var key = pubkeys[i];

        try {
            var signature = new KJUR.crypto.Signature({ 'alg': algorithm });
            signature.init(key);
            signature.updateString(str);
            if (signature.verify(hexsig)) return true;
        } catch (exc) {
        }
    }

    return false;
};
